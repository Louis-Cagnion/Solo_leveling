"""Doublures des tests de T4 : serveur factice de l'API 42, fixtures, navigateur simulé,
horloge factice, capture du journal et garde qui refuse tout hôte hors de 127.0.0.1.

Le serveur écoute sur 127.0.0.1, port 0. Chaque chemin reçoit une suite de réponses
rendues dans l'ordre, la dernière se répète ; un chemin sans route répond 404. Toutes les
requêtes reçues sont enregistrées, et le journal de `http.server` est coupé.
"""

import io
import json
import logging
import os
import socket
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import ProxyHandler, build_opener

HOST = "127.0.0.1"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "api42"
PROXY_VARIABLES = {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}


@dataclass(frozen=True)
class Reply:
    """Réponse rendue par le serveur factice.

    Args:
        status: code HTTP.
        body: octets du corps.
        headers: couples (nom, valeur) d'en-têtes en plus.
        delay: secondes d'attente avant de répondre.
        length: vrai pour envoyer `Content-Length`, faux pour fermer en fin de corps.
    """

    status: int = 200
    body: bytes = b""
    headers: tuple = ()
    delay: float = 0.0
    length: bool = True


@dataclass(frozen=True)
class Request:
    """Requête reçue.

    Args:
        method: `GET` ou `POST`.
        path: chemin sans requête.
        query: dict nom vers liste de valeurs.
        headers: dict des en-têtes, noms en minuscules.
        body: octets du corps.
        at: instant de l'horloge injectée à l'arrivée, ou `None`.
    """

    method: str
    path: str
    query: dict
    headers: dict
    body: bytes
    at: float | None = None


def load(name):
    """Renvoie le contenu JSON de la fixture `tests/fixtures/api42/<name>`."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def json_reply(data, status=200, headers=()):
    """Renvoie une `Reply` JSON.

    Args:
        data: valeur sérialisable ; NaN et infinis sont écrits tels quels.
        status: code HTTP.
        headers: couples (nom, valeur) en plus.

    Returns:
        La `Reply` de type `application/json`.
    """
    return Reply(
        status=status,
        body=json.dumps(data).encode("utf-8"),
        headers=(("Content-Type", "application/json"),) + tuple(headers),
    )


class _Handler(BaseHTTPRequestHandler):
    """Transmet chaque requête au `FakeServer` propriétaire."""

    def log_message(self, format, *args):
        """Coupe le journal par défaut, qui écrirait la ligne de requête."""

    def do_GET(self):
        self.server.owner.answer(self)

    def do_POST(self):
        self.server.owner.answer(self)


@dataclass
class _Route:
    replies: list
    served: int = field(default=0)


class FakeServer:
    """Serveur factice lancé dans un fil, à fermer par `close()` ou `with`.

    Args:
        clock: fonction sans argument qui date chaque requête, ou `None`.
    """

    def __init__(self, clock=None):
        self.clock = clock
        self.routes = {}
        self.received = []
        self.lock = threading.Lock()
        self.httpd = ThreadingHTTPServer((HOST, 0), _Handler)
        self.httpd.daemon_threads = True
        self.httpd.block_on_close = False
        self.httpd.owner = self
        self.thread = threading.Thread(
            target=self.httpd.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        )
        self.thread.start()

    @property
    def url(self):
        """Base `http://127.0.0.1:<port>` du serveur."""
        return f"http://{HOST}:{self.httpd.server_address[1]}"

    def route(self, path, *replies):
        """Associe à `path` les `Reply` rendues dans l'ordre, la dernière répétée."""
        with self.lock:
            self.routes[path] = _Route(list(replies))

    def requests(self, path=None):
        """Renvoie la liste des `Request` reçues, sur `path` seul s'il est donné."""
        with self.lock:
            return [r for r in self.received if path is None or r.path == path]

    def answer(self, handler):
        """Enregistre la requête de `handler` puis écrit la réponse de sa route."""
        parts = urlsplit(handler.path)
        size = int(handler.headers.get("Content-Length") or 0)
        request = Request(
            method=handler.command,
            path=parts.path,
            query=parse_qs(parts.query),
            headers={name.lower(): value for name, value in handler.headers.items()},
            body=handler.rfile.read(size) if size else b"",
            at=self.clock() if self.clock else None,
        )
        with self.lock:
            self.received.append(request)
            route = self.routes.get(parts.path)
            if route is None:
                reply = json_reply({"error": "Not Found"}, status=404)
            else:
                reply = route.replies[min(route.served, len(route.replies) - 1)]
                route.served += 1
        self._write(handler, reply)

    @staticmethod
    def _write(handler, reply):
        """Écrit `reply`, sans erreur si le client a déjà coupé."""
        if reply.delay:
            time.sleep(reply.delay)
        try:
            handler.send_response(reply.status)
            for name, value in reply.headers:
                handler.send_header(name, value)
            if reply.length:
                handler.send_header("Content-Length", str(len(reply.body)))
            handler.end_headers()
            handler.wfile.write(reply.body)
        except OSError:
            pass

    def close(self):
        """Arrête le fil et libère le port."""
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=1)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


class NetworkGuard:
    """Retire les proxys et fait refuser par `socket` tout hôte hors de `HOST`.

    `outside` liste les hôtes refusés depuis le dernier `outside.clear()`.
    """

    def __init__(self):
        self.outside = []
        self.patches = []

    def refuse(self, host):
        """Note `host` et dit s'il faut le refuser."""
        if host in (HOST, None):
            return False
        self.outside.append(host)
        return True

    def start(self):
        """Pose les remplacements de `connect`, `connect_ex` et `getaddrinfo`."""
        connect = socket.socket.connect
        connect_ex = socket.socket.connect_ex
        getaddrinfo = socket.getaddrinfo

        def checked(real):
            def call(sock, address):
                if isinstance(address, tuple) and self.refuse(address[0]):
                    raise OSError(f"test : connexion vers {address[0]} refusée")
                return real(sock, address)
            return call

        def resolve(host, *args, **kwargs):
            if self.refuse(host):
                raise socket.gaierror(f"test : résolution de {host} refusée")
            return getaddrinfo(host, *args, **kwargs)

        env = {k: v for k, v in os.environ.items() if k.lower() not in PROXY_VARIABLES}
        self.patches = [
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(socket.socket, "connect", checked(connect)),
            mock.patch.object(socket.socket, "connect_ex", checked(connect_ex)),
            mock.patch.object(socket, "getaddrinfo", resolve),
        ]
        for patch in self.patches:
            patch.start()

    def stop(self):
        """Rend `socket` et l'environnement d'origine."""
        for patch in reversed(self.patches):
            patch.stop()


def free_port():
    """Renvoie un port de 127.0.0.1 libre à l'instant de l'appel."""
    with socket.socket() as probe:
        probe.bind((HOST, 0))
        return probe.getsockname()[1]


def get_status(url):
    """GET sans proxy : code HTTP reçu, ou nom de l'exception réseau."""
    try:
        with build_opener(ProxyHandler({})).open(url, timeout=1) as response:
            return response.status
    except HTTPError as error:
        error.close()
        return error.code
    except OSError as error:
        return type(error).__name__


def callback_url(port, **params):
    """URL de retour `/callback` sur `port` avec les paramètres donnés."""
    return f"http://{HOST}:{port}/callback?{urlencode(params)}"


def silent_connection(port):
    """Ouvre une connexion vers 127.0.0.1:`port` sans rien y envoyer (préconnexion)."""
    return socket.create_connection((HOST, port), timeout=2)


def dribble(port, data, step, limit):
    """Envoie `data` octet par octet vers 127.0.0.1:`port`, puis ferme la connexion.

    Args:
        port: port TCP de 127.0.0.1.
        data: octets à envoyer un par un.
        step: secondes entre deux octets.
        limit: secondes au plus avant de couper soi-même.

    Returns:
        Le nombre d'octets envoyés ; l'envoi s'arrête dès que le serveur coupe.
    """
    sent = 0
    begin = time.monotonic()
    with socket.create_connection((HOST, port), timeout=2) as client:
        for index in range(len(data)):
            if time.monotonic() - begin >= limit:
                break
            try:
                client.sendall(data[index : index + 1])
            except OSError:
                break
            sent += 1
            time.sleep(step)
    return sent


def in_thread(target):
    """Lance `target` dans un fil démon et le renvoie."""
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


class FakeClock:
    """Horloge factice : `sleep` note la durée et avance `now` d'autant."""

    def __init__(self, start=1000.0):
        self.current = start
        self.sleeps = []

    def now(self):
        return self.current

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.current += max(seconds, 0)


class Browser:
    """Navigateur simulé, passé en `open_browser` : il rejoue le retour OAuth.

    Args:
        code: code d'autorisation renvoyé.
        act: faux pour un consentement jamais donné.
        times: nombre d'envois du même retour.
        params: paramètres qui remplacent `code` et `state` ; `None` retire la clé.
    """

    def __init__(self, code, act=True, times=1, params=None):
        self.code = code
        self.act = act
        self.times = times
        self.params = params or {}
        self.urls = []
        self.statuses = []
        self.threads = []

    def __call__(self, url):
        self.urls.append(url)
        if self.act:
            self.threads.append(in_thread(lambda: self.consent(url)))
        return True

    def consent(self, url):
        """Envoie `times` fois le retour vers le `redirect_uri` de `url`."""
        query = parse_qs(urlsplit(url).query)
        params = {"code": self.code, "state": query["state"][0]}
        params.update(self.params)
        params = {key: value for key, value in params.items() if value is not None}
        target = f"{query['redirect_uri'][0]}?{urlencode(params)}"
        for _ in range(self.times):
            self.statuses.append(get_status(target))

    def join(self):
        for thread in self.threads:
            thread.join(timeout=2)


class Capture:
    """Contexte qui capture le journal (tous niveaux), la sortie et l'erreur standard.

    `text` rend tout ce qui a été capturé, traces comprises.
    """

    def __enter__(self):
        self.handler = logging.Handler(logging.DEBUG)
        self.lines = []
        self.handler.emit = lambda record: self.lines.append(self.handler.format(record))
        self.root = logging.getLogger()
        self.level = self.root.level
        self.root.addHandler(self.handler)
        self.root.setLevel(logging.DEBUG)
        self.out, self.err = io.StringIO(), io.StringIO()
        self.redirects = [redirect_stdout(self.out), redirect_stderr(self.err)]
        for redirect in self.redirects:
            redirect.__enter__()
        return self

    def __exit__(self, *exc_info):
        for redirect in reversed(self.redirects):
            redirect.__exit__(*exc_info)
        self.root.removeHandler(self.handler)
        self.root.setLevel(self.level)

    @property
    def text(self):
        return "\n".join(self.lines) + self.out.getvalue() + self.err.getvalue()
