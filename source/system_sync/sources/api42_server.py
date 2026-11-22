"""Serveur de retour OAuth de l'API 42 (T4, A15) : 127.0.0.1 seulement, délai total borné.

Chaque connexion est servie dans son propre fil, avec un délai de socket court : une
préconnexion muette du navigateur ne bloque donc pas le vrai retour. À la fin de l'attente,
le port est fermé, chaque connexion encore ouverte est coupée et son fil attendu. Le journal
de `http.server` est coupé (la ligne de requête porte le code) ; le `state` est comparé en
temps constant. Contrat : `tests/system_sync/sources/test_api42.py` et `test_api42_review.py`.
"""

import contextlib
import hmac
import logging
import socket
import sys
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from system_sync.sources.api42_profile import is_number, preview

HOST = "127.0.0.1"
CALLBACK_PATH = "/callback"
# Délai propre à chaque opération du socket d'une connexion du navigateur.
CONNECTION_TIMEOUT = 5.0
# Secondes entre deux contrôles de la demande d'arrêt par `serve_forever`.
POLL_INTERVAL = 0.05
LOGGER = logging.getLogger(__name__)


def single(query, name):
    """Lit un paramètre présent une seule fois dans une requête analysée.

    Args:
        query: dict nom vers liste de valeurs (`parse_qs`).
        name: nom du paramètre.

    Returns:
        La valeur, ou `None` si le paramètre manque ou se répète.
    """
    values = query.get(name, [])
    return values[0] if len(values) == 1 else None


@dataclass(frozen=True)
class Callback:
    """Issue de l'attente du retour OAuth.

    Args:
        code: code d'autorisation reçu, ou `None` ; jamais rendu par `repr`.
        error: `None` si `code`, sinon la cause (délai écoulé, `error` reçue de l'API).
    """

    code: str | None = field(default=None, repr=False)
    error: str | None = None


class LoopbackServer(ThreadingHTTPServer):
    """Serveur HTTP à un fil démon par connexion, sans partage de port ni trace d'erreur.

    Args:
        address: couple (hôte, port) à lier.
        handler: classe de `BaseHTTPRequestHandler`.
    """

    allow_reuse_port = False

    def __init__(self, address, handler):
        super().__init__(address, handler)
        self.lock = threading.Lock()
        self.connections = {}

    def process_request(self, request, client_address):
        """Sert `request` dans un fil démon, noté avant son départ pour `close_connections`."""
        thread = threading.Thread(
            target=self.process_request_thread,
            args=(request, client_address),
            daemon=True,
        )
        with self.lock:
            self.connections[request] = thread
        thread.start()

    def shutdown_request(self, request):
        """Oublie `request` puis la ferme ; l'oubli précède la fermeture, sous verrou."""
        with self.lock:
            self.connections.pop(request, None)
        super().shutdown_request(request)

    def close_connections(self):
        """Coupe chaque connexion encore ouverte, puis attend son fil au plus le délai."""
        with self.lock:
            threads = list(self.connections.values())
            for request in self.connections:
                with contextlib.suppress(OSError):
                    request.shutdown(socket.SHUT_RDWR)
        for thread in threads:
            thread.join(CONNECTION_TIMEOUT)
            if thread.is_alive():
                LOGGER.warning("API 42 : fil d'une connexion encore actif après fermeture")

    def handle_error(self, request, client_address):
        """Journalise une requête interrompue sans trace, qui pourrait citer le code."""
        LOGGER.warning(
            "API 42 : requête du navigateur interrompue (%s)",
            type(sys.exception()).__name__,
        )


class CallbackHandler(BaseHTTPRequestHandler):
    """Répond au navigateur pour le `CallbackServer` qui porte le serveur."""

    timeout = CONNECTION_TIMEOUT

    def log_message(self, format, *args):
        """Coupe le journal de `http.server`, qui écrirait la ligne de requête et le code."""

    def do_GET(self):
        """Juge la requête puis écrit une page texte sans ressource externe."""
        owner = self.server.owner
        reply = owner.receive(self.path)
        if reply is None:
            return
        status, text, final = reply
        body = text.encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)
        finally:
            if final:
                owner.finish()


class CallbackServer:
    """Serveur de retour OAuth sur 127.0.0.1 : un seul retour accepté, délai total borné.

    `start()` lie le port, `wait()` sert jusqu'au premier retour `/callback` dont le
    `state` est égal (temps constant) ou jusqu'au délai, puis ferme le port. Une seule
    attente par serveur.

    Args:
        port: entier, port TCP de 127.0.0.1.
        state: texte attendu dans le paramètre `state`.
        timeout: secondes réelles d'attente au plus, nombre fini positif.
    """

    def __init__(self, port, state, timeout):
        self.port = port
        self.timeout = timeout
        self._state = state.encode("utf-8")
        self._httpd = None
        self._serving = None
        self._callback = None
        self._closed = False
        self._lock = threading.Lock()
        self._done = threading.Event()

    @property
    def address(self):
        """Couple (hôte, port) du socket à l'écoute, ou `None` hors écoute."""
        return self._httpd.socket.getsockname() if self._httpd else None

    def start(self):
        """Lie 127.0.0.1:`port`, sans jamais toucher à un éventuel occupant.

        Returns:
            `None` si le serveur écoute, sinon l'erreur qui nomme le port et la cause.
        """
        if self._httpd is not None:
            return None
        try:
            self._httpd = LoopbackServer((HOST, self.port), CallbackHandler)
        except (OverflowError, TypeError):
            return f"port {self.port!r} invalide : entier de 0 à 65535 attendu"
        except OSError as error:
            return f"port {self.port} de {HOST} indisponible : {error.strerror}"
        self._httpd.owner = self
        return None

    def receive(self, target):
        """Juge une requête du navigateur et retient le premier retour valide.

        Args:
            target: chemin et requête de la ligne HTTP, texte.

        Returns:
            Triplet (statut HTTP, texte de la page, vrai si ce retour clôt l'attente), ou
            `None` si l'attente est déjà close (rien à écrire).
        """
        parts = urlsplit(target)
        if parts.path != CALLBACK_PATH:
            return 404, "Adresse inconnue.", False
        query = parse_qs(parts.query)
        state = single(query, "state")
        if  state is None \
            or not hmac.compare_digest(state.encode("utf-8"), self._state):
            return 400, "Paramètre state absent ou différent : retour ignoré.", False
        error = single(query, "error")
        code = single(query, "code")
        if error is None and not code:
            return 400, "Paramètre code absent : retour ignoré.", False
        with self._lock:
            if self._closed:
                return None
            if self._callback is not None:
                return 409, "Retour déjà reçu : celui-ci est ignoré.", False
            if error is not None:
                cause = f"consentement refusé par l'API 42 (error={preview(error)})"
                self._callback = Callback(error=cause)
                return 200, "Consentement refusé ; vous pouvez fermer cet onglet.", True
            self._callback = Callback(code=code)
        return 200, "Consentement reçu ; vous pouvez fermer cet onglet.", True

    def finish(self):
        """Signale à `wait()` que le retour qui clôt l'attente a reçu sa page."""
        self._done.set()

    def wait(self):
        """Sert jusqu'au premier retour valide ou jusqu'au délai, puis ferme le port.

        Returns:
            `Callback` avec le code, ou avec la cause de l'échec.
        """
        if self._httpd is None:
            return Callback(error="serveur de retour non démarré : start() à appeler d'abord")
        if not is_number(self.timeout) or self.timeout <= 0:
            self.close()
            return Callback(error=f"délai de consentement {preview(self.timeout)} invalide")
        serving = threading.Thread(
            target=self._httpd.serve_forever,
            kwargs={"poll_interval": POLL_INTERVAL},
            daemon=True,
        )
        try:
            serving.start()
        except RuntimeError as error:
            self.close()
            return Callback(error=f"fil du serveur de retour non lancé : {error}")
        self._serving = serving
        try:
            self._done.wait(min(self.timeout, threading.TIMEOUT_MAX))
        finally:
            self.close()
        return self._callback or Callback(error=f"aucun retour valide en {self.timeout} s")

    def close(self):
        """Ferme le port, coupe les connexions et attend leurs fils ; rien hors écoute."""
        if self._httpd is None:
            return
        with self._lock:
            self._closed = True
        if self._serving is not None:
            self._httpd.shutdown()
            self._serving.join()
            self._serving = None
        self._httpd.close_connections()
        self._httpd.server_close()
        self._httpd = None
