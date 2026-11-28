"""Client de l'API 42 (T4) : consentement OAuth, lecture de `/v2/me` et des achievements.

Flux authorization code (A15) : un serveur de retour sur 127.0.0.1 (`api42_server.py`)
reçoit le code, échangé contre un jeton gardé en mémoire seulement. Chaque requête passe
par un limiteur de 2 par seconde, porte un délai, refuse un corps trop gros et reprend au
plus quelques fois sur 429 et 5xx. De `/v2/me` ne sortent que le niveau du cursus 21, les
projets validés et les achievements (liste blanche, `conception.md:33` ;
`api42_profile.py`), écrits ensuite dans un cache atomique (`api42_cache.py`). Aucune
fonction publique ne lève ; le secret, le code et le jeton ne vont ni au journal, ni au
cache, ni dans un message. Contrat : `tests/system_sync/sources/test_api42.py` ;
dépendance décrite dans `EXTERNAL.md`.
"""

import http.client
import json
import logging
import re
import secrets
import ssl
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from system_sync.config import PORTS
from system_sync.sources.api42_cache import cache_payload, fall_back, write_cache
from system_sync.sources.api42_profile import (
    ACHIEVEMENTS_PATH,
    ME_PATH,
    Api42Result,
    build_result,
    is_integer,
    is_number,
    me_problem,
    preview,
)
from system_sync.sources.api42_server import (
    CALLBACK_PATH,
    HOST,
    Callback,
    CallbackServer,
)

__all__ = [
    "API_BASE",
    "Api42Client",
    "Api42Result",
    "Callback",
    "CallbackServer",
    "Fetch",
    "RateLimiter",
    "authorization_url",
    "read_api42",
]

API_BASE = "https://api.intra.42.fr"
TOKEN_PATH = "/oauth/token"
CREDENTIALS = ("API42_CLIENT_ID", "API42_CLIENT_SECRET")
PORT_VARIABLE = "API42_CALLBACK_PORT"
# En-tête générique de chaque requête : sans lui, le pare-feu du service refuse (erreur 1010).
USER_AGENT = "progression-system-sync/1.0"
PAGE_SIZE = 100
STATE_BYTES = 32
DEFAULT_RATE = 2.0
CONSENT_TIMEOUT = 120.0
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 2
MAX_RETRY_AFTER = 10.0
DEFAULT_RETRY_PAUSE = 1.0
MAX_PAGES = 20
MAX_BYTES = 5_000_000
DIGITS = re.compile(r"[0-9]{1,12}")
# Jeton émis par l'API : caractères ASCII visibles seulement, sans quoi l'en-tête casse.
TOKEN_PATTERN = re.compile(r"[\x21-\x7e]+")
# Cause d'un statut HTTP d'échec ; un statut absent prend celle de sa centaine.
HTTP_CAUSES = {
    401: "authentification refusée (identifiants ou jeton invalides)",
    403: "accès refusé (scope insuffisant ou requête bloquée par le pare-feu du service)",
    404: "ressource introuvable",
    429: "quota de requêtes dépassé",
}
CLASS_CAUSES = {
    3: "redirection non suivie",
    4: "requête refusée",
    5: "erreur du serveur",
}
LOGGER = logging.getLogger(__name__)


def digits(text):
    """Convertit strictement un en-tête numérique (`Retry-After`, `Content-Length`).

    Args:
        text: valeur d'en-tête, texte ou `None`.

    Returns:
        L'entier écrit en chiffres ASCII seuls, ou `None`.
    """
    if  text is None \
        or not DIGITS.fullmatch(text.strip()):
        return None
    return int(text)


def redirect_uri(port):
    """Construit l'URI de retour déclarée à l'API (A15).

    Args:
        port: entier, port de 127.0.0.1.

    Returns:
        `http://127.0.0.1:<port>/callback`.
    """
    return f"http://{HOST}:{port}{CALLBACK_PATH}"


def authorization_url(client_id, port):
    """Construit l'URL de consentement et son `state` aléatoire.

    Args:
        client_id: identifiant de l'application, texte non vide.
        port: entier, port du serveur de retour.

    Returns:
        Couple (URL `API_BASE/oauth/authorize?...`, `state` URL-safe de 256 bits).
    """
    state = secrets.token_urlsafe(STATE_BYTES)
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri(port),
            "response_type": "code",
            "state": state,
        }
    )
    return f"{API_BASE}/oauth/authorize?{query}", state


class RateLimiter:
    """Limiteur de débit : au plus `rate` passages par seconde de `clock`.

    Args:
        rate: passages par seconde, nombre fini positif (sinon `DEFAULT_RATE`, signalé).
        clock: fonction sans argument qui rend des secondes croissantes.
        sleep: fonction qui attend un nombre de secondes.
    """

    def __init__(self, rate=DEFAULT_RATE, clock=time.monotonic, sleep=time.sleep):
        if not is_number(rate) or rate <= 0:
            LOGGER.warning(
                "API 42 : débit %s invalide, %s requêtes par seconde retenues",
                preview(rate),
                DEFAULT_RATE,
            )
            rate = DEFAULT_RATE
        self.interval = 1.0 / rate
        self.clock = clock
        self.sleep = sleep
        self._last = None

    def wait(self):
        """Attend par `sleep` le reste de l'intervalle depuis le passage précédent."""
        if self._last is not None:
            pause = self._last + self.interval - self.clock()
            if pause > 0:
                self.sleep(pause)
        self._last = self.clock()


@dataclass(frozen=True)
class Fetch:
    """Résultat d'une lecture de l'API.

    Args:
        data: JSON décodé (pages fusionnées en liste), ou `None` en cas d'erreur.
        error: `None`, ou la cause avec le chemin et, s'il y en a un, le code HTTP.
    """

    data: object = None
    error: str | None = None


class NoRedirect(HTTPRedirectHandler):
    """Ne suit aucune redirection : la réponse 3xx remonte en `HTTPError`."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Refuse la redirection vers `newurl`, quel qu'en soit l'hôte."""
        return None


def http_error(path, status):
    """Rend le message d'un statut HTTP d'échec, sans jamais citer le corps reçu.

    Args:
        path: chemin d'API, texte.
        status: code HTTP entier.

    Returns:
        `<chemin> : HTTP <code>, <cause>`.
    """
    cause = HTTP_CAUSES.get(status) or CLASS_CAUSES.get(status // 100, "statut inattendu")
    return f"{path} : HTTP {status}, {cause}"


def refused_base(api_base):
    """Dit pourquoi refuser une base qui enverrait le secret en clair.

    Args:
        api_base: base de l'API, texte.

    Returns:
        `None` pour `https://` ou `http://127.0.0.1`, sinon la cause du refus.
    """
    parts = urlsplit(api_base)
    if  parts.scheme == "https" \
        or (parts.scheme == "http"
            and parts.hostname == HOST):
        return None
    return f"base {preview(api_base)} refusée : https attendu (http vers {HOST} seul)"


class Api42Client:
    """Client HTTP de l'API 42 : jeton en mémoire, débit, délais et reprises bornés.

    Args:
        api_base: base `https://...` de l'API (http seulement vers 127.0.0.1).
        timeout: secondes de délai de chaque requête, nombre positif.
        limiter: `RateLimiter`, ou `None` pour un limiteur par défaut.
        sleep: fonction qui attend un nombre de secondes, pour les reprises.
        max_retries: entier, reprises au plus après un 429 ou un 5xx.
        max_retry_after: secondes d'attente au plus avant une reprise.
        max_pages: entier, pages de `/v2/achievements` lues au plus.
        max_bytes: entier, octets au plus par corps de réponse.
    """

    def __init__(
        self,
        api_base,
        *,
        timeout=REQUEST_TIMEOUT,
        limiter=None,
        sleep=time.sleep,
        max_retries=MAX_RETRIES,
        max_retry_after=MAX_RETRY_AFTER,
        max_pages=MAX_PAGES,
        max_bytes=MAX_BYTES,
    ):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.limiter = limiter or RateLimiter()
        self.sleep = sleep
        self.max_retries = max(max_retries, 0)
        self.max_retry_after = max(max_retry_after, 0)
        self.max_pages = max_pages
        self.max_bytes = max_bytes
        self._token = None
        self._refused_base = refused_base(self.api_base)
        self._opener = build_opener(
            HTTPSHandler(context=ssl.create_default_context()),
            NoRedirect,
        )

    def exchange_code(self, client_id, client_secret, code, redirect_uri):
        """Échange le code d'autorisation contre un jeton, gardé en mémoire.

        Args:
            client_id: identifiant de l'application, texte.
            client_secret: secret de l'application, texte.
            code: code reçu par le serveur de retour, texte.
            redirect_uri: URI de retour déclarée, texte.

        Returns:
            `None` si le jeton est obtenu, sinon l'erreur (sans aucun secret).
        """
        form = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        fetch = self._request(TOKEN_PATH, form=form)
        if fetch.error is not None:
            return fetch.error
        token = fetch.data.get("access_token") if isinstance(fetch.data, dict) else None
        if not isinstance(token, str):
            return f"{TOKEN_PATH} : réponse sans access_token"
        if not TOKEN_PATTERN.fullmatch(token):
            return f"{TOKEN_PATH} : access_token de forme inattendue"
        self._token = token
        return None

    def fetch_me(self):
        """Lit `GET /v2/me`.

        Returns:
            `Fetch` du JSON reçu, non encore contrôlé.
        """
        return self._request(ME_PATH)

    def fetch_achievements(self):
        """Lit `GET /v2/achievements` page par page, jusqu'à la première incomplète.

        Returns:
            `Fetch` de la liste fusionnée, ou erreur au-delà de `max_pages` pages.
        """
        items = []
        for number in range(1, self.max_pages + 1):
            fetch = self._request(ACHIEVEMENTS_PATH, {"per_page": PAGE_SIZE, "page": number})
            if fetch.error is not None:
                return Fetch(error=f"{fetch.error} (page {number})")
            if not isinstance(fetch.data, list):
                kind = type(fetch.data).__name__
                cause = f"page {number} en {kind}, liste attendue"
                return Fetch(error=f"{ACHIEVEMENTS_PATH} : {cause}")
            items.extend(fetch.data)
            if len(fetch.data) < PAGE_SIZE:
                LOGGER.info(
                    "API 42 : %s lu, %d éléments sur %d pages",
                    ACHIEVEMENTS_PATH,
                    len(items),
                    number,
                )
                return Fetch(data=items)
        cause = f"plafond de {self.max_pages} pages pleines atteint"
        return Fetch(error=f"{ACHIEVEMENTS_PATH} : {cause}")

    def _request(self, path, query=None, form=None):
        """Envoie une requête, reprise au plus `max_retries` fois sur 429 et 5xx.

        Args:
            path: chemin d'API, texte.
            query: dict des paramètres d'URL, ou `None`.
            form: dict du formulaire envoyé en POST, ou `None` pour un GET.

        Returns:
            `Fetch` de la dernière tentative.
        """
        if self._refused_base is not None:
            return Fetch(error=f"{path} : {self._refused_base}")
        url = self.api_base + path + (f"?{urlencode(query)}" if query else "")
        attempts = self.max_retries + 1
        for attempt in range(1, attempts + 1):
            fetch, pause = self._attempt(url, path, form)
            if pause is None:
                return fetch
            if attempt < attempts:
                LOGGER.warning(
                    "API 42 : %s ; nouvelle tentative dans %.1f s",
                    fetch.error,
                    pause,
                )
                self.sleep(pause)
        return Fetch(error=f"{fetch.error} ({attempts} tentatives)")

    def _attempt(self, url, path, form):
        """Joue une tentative après le limiteur.

        Args:
            url: URL complète, texte.
            path: chemin d'API, texte, pour les messages.
            form: dict du formulaire POST, ou `None`.

        Returns:
            Couple (`Fetch`, pause avant reprise en secondes, ou `None` si rien à reprendre).
        """
        self.limiter.wait()
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        data = urlencode(form).encode("utf-8") if form else None
        request = Request(url, data=data, headers=headers)
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                return self._decode(path, response), None
        except HTTPError as error:
            retry_after = error.headers.get("Retry-After") if error.headers else None
            error.close()
            fetch = Fetch(error=http_error(path, error.code))
            if error.code == 429 or error.code >= 500:
                return fetch, self._pause(retry_after)
            return fetch, None
        except URLError as error:
            if isinstance(error.reason, TimeoutError):
                return Fetch(error=f"{path} : aucune réponse en {self.timeout} s"), None
            return Fetch(error=f"{path} : connexion impossible ({error.reason})"), None
        except TimeoutError:
            return Fetch(error=f"{path} : réponse non terminée en {self.timeout} s"), None
        except (OSError, http.client.HTTPException) as error:
            return Fetch(error=f"{path} : réponse interrompue ({type(error).__name__})"), None

    def _pause(self, retry_after):
        """Renvoie l'attente avant reprise : `Retry-After` en secondes, plafonné.

        Args:
            retry_after: valeur de l'en-tête, texte ou `None`.

        Returns:
            Secondes entre 0 et `max_retry_after` (`DEFAULT_RETRY_PAUSE` si illisible).
        """
        seconds = digits(retry_after)
        wanted = DEFAULT_RETRY_PAUSE if seconds is None else seconds
        return min(wanted, self.max_retry_after)

    def _decode(self, path, response):
        """Lit un corps de réponse borné et le décode en JSON.

        Args:
            path: chemin d'API, texte, pour les messages.
            response: réponse HTTP ouverte.

        Returns:
            `Fetch` du JSON, ou la cause du refus (taille, type, encodage, syntaxe).
        """
        declared = digits(response.headers.get("Content-Length"))
        if declared is not None and declared > self.max_bytes:
            cause = f"corps annoncé de {declared} octets, plafond {self.max_bytes}"
            return Fetch(error=f"{path} : {cause}")
        body = response.read(self.max_bytes + 1)
        if len(body) > self.max_bytes:
            return Fetch(error=f"{path} : corps de plus de {self.max_bytes} octets")
        kind = response.headers.get("Content-Type")
        if kind is not None and "json" not in kind.lower():
            return Fetch(error=f"{path} : type {preview(kind)} reçu, JSON attendu")
        try:
            return Fetch(data=json.loads(body.decode("utf-8-sig")))
        except UnicodeDecodeError as error:
            return Fetch(error=f"{path} : octet non UTF-8 à l'offset {error.start}")
        except json.JSONDecodeError as error:
            place = f"ligne {error.lineno}, colonne {error.colno}"
            return Fetch(error=f"{path} : JSON invalide ({place} : {error.msg})")
        except (ValueError, RecursionError) as error:
            return Fetch(error=f"{path} : JSON inexploitable ({type(error).__name__})")


def env_problem(env):
    """Contrôle les variables `API42_*` du dict de `check_env`, sans citer leur valeur.

    Args:
        env: dict de `config.check_env` ; seules les clés `API42_*` sont lues.

    Returns:
        `None` si elles sont utilisables, sinon la cause qui nomme chaque variable fautive.
    """
    causes = [
        f"{name} vide ou absente"
        for name in CREDENTIALS
        if not isinstance(env.get(name), str)
           or not env.get(name).strip()
    ]
    port = env.get(PORT_VARIABLE)
    if port is None:
        causes.append(f"{PORT_VARIABLE} vide ou absente")
    elif not is_integer(port) or port not in PORTS:
        bounds = f"entier de {PORTS.start} à {PORTS.stop - 1} attendu"
        causes.append(f"{PORT_VARIABLE} invalide ({preview(port)}) : {bounds}")
    return f"API 42 non configurée (.env) : {', '.join(causes)}" if causes else None


def consent(env, open_browser, consent_timeout):
    """Ouvre la page de consentement et attend le retour sur le port de `env`.

    Args:
        env: dict des variables `API42_*` déjà contrôlées.
        open_browser: fonction URL vers booléen, faux si aucun navigateur ne s'ouvre.
        consent_timeout: secondes réelles d'attente au plus.

    Returns:
        `Callback` avec le code, ou avec la cause de l'échec.
    """
    port = env[PORT_VARIABLE]
    url, state = authorization_url(env["API42_CLIENT_ID"], port)
    server = CallbackServer(port, state, consent_timeout)
    error = server.start()
    if error is not None:
        return Callback(error=error)
    LOGGER.info("API 42 : serveur de retour à l'écoute sur %s:%s", HOST, port)
    try:
        opened = open_browser(url)
    except (webbrowser.Error, OSError) as failure:
        opened = False
        LOGGER.warning(
            "API 42 : ouverture du navigateur en échec (%s)",
            type(failure).__name__,
        )
    if not opened:
        server.close()
        return Callback(error="aucun navigateur n'a pu ouvrir la page de consentement")
    LOGGER.info("API 42 : consentement attendu au plus %s s", consent_timeout)
    return server.wait()


def read_api42(
    env,
    cache_path,
    *,
    open_browser=webbrowser.open,
    api_base=API_BASE,
    consent_timeout=CONSENT_TIMEOUT,
    request_timeout=REQUEST_TIMEOUT,
    clock=time.monotonic,
    sleep=time.sleep,
):
    """Lit le niveau, les projets et les achievements de l'API 42, avec repli sur le cache.

    Args:
        env: dict de `config.check_env` ; seules les clés `API42_*` sont lues.
        cache_path: chemin du cache JSON, écrit seulement après une lecture `ok`.
        open_browser: fonction URL vers booléen qui ouvre la page de consentement.
        api_base: base de l'API, `API_BASE` hors tests.
        consent_timeout: secondes réelles d'attente du consentement au plus.
        request_timeout: secondes de délai de chaque requête.
        clock: horloge du limiteur, fonction sans argument.
        sleep: attente du limiteur et des reprises, fonction de secondes.

    Returns:
        `Api42Result` `ok`, sinon `cache` (cache relu) ou `unavailable`.
    """
    cache_path = Path(cache_path)
    problem = env_problem(env)
    if problem is not None:
        return fall_back(cache_path, problem)
    callback = consent(env, open_browser, consent_timeout)
    if callback.error is not None:
        return fall_back(cache_path, callback.error)
    client = Api42Client(
        api_base,
        timeout=request_timeout,
        limiter=RateLimiter(clock=clock, sleep=sleep),
        sleep=sleep,
    )
    error = client.exchange_code(
        env["API42_CLIENT_ID"],
        env["API42_CLIENT_SECRET"],
        callback.code,
        redirect_uri(env[PORT_VARIABLE]),
    )
    if error is not None:
        return fall_back(cache_path, error)
    LOGGER.info("API 42 : jeton obtenu")
    me = client.fetch_me()
    error = me.error or me_problem(me.data)
    if error is not None:
        return fall_back(cache_path, error)
    result = build_result(me.data, client.fetch_achievements())
    LOGGER.info(
        "API 42 : %d éléments lus, %d écartés, %d projets validés, %d achievements",
        result.read,
        result.rejected,
        len(result.projects),
        len(result.achievements),
    )
    error = write_cache(cache_path, cache_payload(result))
    if error is None:
        LOGGER.info("API 42 : cache %s écrit", cache_path)
    else:
        LOGGER.warning("API 42 : %s", error)
    return result
