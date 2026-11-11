"""Chargement et contrôle de `config/rules.toml` et de `.env`.

Chaque erreur est une `ConfigError` à message unique par cause : elle nomme le
fichier, la ligne quand elle est connue, la clé et la valeur reçue. La valeur
d'un secret n'apparaît jamais dans un message.
"""

import hashlib
import re
import tomllib
from pathlib import Path

ENV_VARIABLES = (
    "PROFESSOR_SUIVI_DIR",
    "IA_HISTORY_CSV",
    "API42_CLIENT_ID",
    "API42_CLIENT_SECRET",
    "API42_CALLBACK_PORT",
)
REQUIRED_PATHS = ("PROFESSOR_SUIVI_DIR", "IA_HISTORY_CSV")
FAMILIES = ("states", "ranks", "ia", "xp_table", "calibration", "titles")
IA_RATES = ("louis", "mixte", "ia")
PORT_RANGE = (1024, 65535)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class ConfigError(Exception):
    """Configuration illisible ou invalide."""


def _read_bytes(path):
    """Lit un fichier de configuration, ou lève une erreur qui nomme le chemin."""
    path = Path(path)
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise ConfigError(f"{path} : fichier absent") from None
    except OSError as error:
        raise ConfigError(f"{path} : lecture impossible ({error.strerror})") from None


def _decode(path, raw):
    """Décode en UTF-8 en ignorant un éventuel BOM."""
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ConfigError(f"{path} : octet non UTF-8 à la position {error.start}") from None


def rules_fingerprint(path):
    """Renvoie le sha256 hexadécimal des octets du fichier de règles."""
    return hashlib.sha256(_read_bytes(path)).hexdigest()


def _locate(lines, section, key):
    """Renvoie le numéro de la ligne de `key` dans `[section]`, ou None."""
    header = re.compile(r"^\s*\[\s*" + re.escape(section) + r"\s*\]")
    key_line = re.compile(r"^\s*" + re.escape(key) + r"\s*=")
    inside = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("["):
            inside = bool(header.match(line))
        elif inside and key_line.match(line):
            return number
    return None


class _Rules:
    """Contrôle d'un `rules.toml` déjà analysé, avec localisation des lignes."""

    def __init__(self, path, text, data):
        self.path = path
        self.lines = text.splitlines()
        self.data = data

    def fail(self, section, key, problem, value=None):
        """Lève l'erreur avec fichier, ligne, clé et valeur reçue."""
        number = _locate(self.lines, section, key)
        where = f"{self.path}:{number}" if number else str(self.path)
        message = f"{where} : clé `{section}.{key}` {problem}"
        if value is not None:
            message += f" (valeur reçue : {value!r})"
        raise ConfigError(message)

    def table(self, name):
        """Renvoie la famille `name`, qui doit être une table non vide."""
        value = self.data.get(name)
        if value is None:
            raise ConfigError(f"{self.path} : famille `{name}` absente")
        if not isinstance(value, dict) or not value:
            raise ConfigError(f"{self.path} : famille `{name}` vide ou mal typée")
        return value

    def check_states(self):
        states = self.table("states")
        order = states.get("order")
        if not isinstance(order, list) or not all(isinstance(s, str) for s in order):
            self.fail("states", "order", "doit être une liste de textes", order)
        seen = set()
        for state in order:
            if state in seen:
                self.fail("states", "order", "contient un état en double", state)
            seen.add(state)
        for state in states.get("excluded", []):
            if state not in seen:
                self.fail("states", "excluded", "nomme un état hors de `order`", state)

    def check_typed(self, family):
        """Chaque rang ou titre est une table avec un `type` textuel."""
        for name, entry in self.table(family).items():
            kind = entry.get("type") if isinstance(entry, dict) else None
            if not isinstance(kind, str) or not kind:
                self.fail(f"{family}.{name}", "type", "doit être un texte non vide", kind)

    def check_ia(self):
        ia = self.table("ia")
        for name in IA_RATES:
            if name not in ia:
                self.fail("ia", name, "est absente")
            rate = ia[name]
            valid = isinstance(rate, (int, float)) and not isinstance(rate, bool)
            if not valid or not 0 <= rate <= 1:
                self.fail("ia", name, "doit être un taux entre 0 et 1", rate)

    def check_xp_table(self):
        table = self.table("xp_table")
        for key in ("url", "commit", "sha256"):
            if not isinstance(table.get(key), str) or not table[key]:
                self.fail("xp_table", key, "doit être un texte non vide", table.get(key))
        if table["commit"] not in table["url"]:
            self.fail("xp_table", "url", "doit contenir le commit épinglé", table["url"])
        if not SHA256_PATTERN.fullmatch(table["sha256"]):
            self.fail("xp_table", "sha256", "doit avoir 64 hexadécimaux", table["sha256"])

    def check_calibration(self):
        calibration = self.table("calibration")
        for key in ("target_level", "min_projects", "min_days"):
            value = calibration.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                self.fail("calibration", key, "doit être un entier positif", value)
        initial = calibration.get("r_initial")
        if not isinstance(initial, (int, float)) or isinstance(initial, bool):
            self.fail("calibration", "r_initial", "doit être un nombre", initial)
        if initial < 0:
            self.fail("calibration", "r_initial", "ne peut pas être négatif", initial)


def load_rules(path):
    """Charge `rules.toml`, le valide et renvoie le dictionnaire des six familles."""
    path = Path(path)
    text = _decode(path, _read_bytes(path))
    if not text.strip():
        raise ConfigError(f"{path} : fichier vide")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"{path} : TOML mal formé, {error}") from None
    rules = _Rules(path, text, data)
    rules.check_states()
    rules.check_typed("ranks")
    rules.check_typed("titles")
    rules.check_ia()
    rules.check_xp_table()
    rules.check_calibration()
    return data


def _unquote(value):
    """Retire une paire de guillemets simples ou doubles autour d'une valeur."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_env(path):
    """Lit un fichier `.env` : `CLE=valeur`, commentaires `#` et lignes vides permis."""
    path = Path(path)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        names = ", ".join(ENV_VARIABLES)
        raise ConfigError(f"{path} : fichier absent ; variables attendues : {names}") from None
    except OSError as error:
        raise ConfigError(f"{path} : lecture impossible ({error.strerror})") from None
    env = {}
    first_seen = {}
    for number, line in enumerate(_decode(path, raw).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key:
            raise ConfigError(f"{path}:{number} : ligne sans `CLE=valeur` ({key!r})")
        if key not in ENV_VARIABLES:
            raise ConfigError(f"{path}:{number} : variable inconnue `{key}`")
        if key in env:
            raise ConfigError(
                f"{path}:{number} : clé `{key}` en doublon "
                f"(déjà définie ligne {first_seen[key]})"
            )
        env[key] = _unquote(value.strip())
        first_seen[key] = number
    return env


def _check_port(text):
    """Convertit strictement le port, ou lève une erreur qui cite la valeur."""
    low, high = PORT_RANGE
    if not re.fullmatch(r"[0-9]+", text) or not low <= int(text) <= high:
        raise ConfigError(
            f"API42_CALLBACK_PORT : port invalide, entier de {low} à {high} attendu "
            f"(valeur reçue : {text!r})"
        )
    return int(text)


def _check_suivi_dir(text):
    """Le dossier du suivi doit exister et être un dossier."""
    path = Path(text).expanduser()
    if not path.exists():
        raise ConfigError(f"PROFESSOR_SUIVI_DIR : chemin inexistant ({path})")
    if not path.is_dir():
        raise ConfigError(f"PROFESSOR_SUIVI_DIR : fichier au lieu d'un dossier ({path})")
    return path


def check_env(env):
    """Contrôle et convertit les variables : chemins en `Path`, port en `int`.

    Les deux chemins sont obligatoires. Les variables de l'API 42 peuvent rester
    vides : le port vaut alors `None`.
    """
    for name in REQUIRED_PATHS:
        if not env.get(name, "").strip():
            raise ConfigError(f"{name} : variable obligatoire absente ou vide")
    port = env.get("API42_CALLBACK_PORT", "").strip()
    return {
        "PROFESSOR_SUIVI_DIR": _check_suivi_dir(env["PROFESSOR_SUIVI_DIR"].strip()),
        "IA_HISTORY_CSV": Path(env["IA_HISTORY_CSV"].strip()).expanduser(),
        "API42_CLIENT_ID": env.get("API42_CLIENT_ID", ""),
        "API42_CLIENT_SECRET": env.get("API42_CLIENT_SECRET", ""),
        "API42_CALLBACK_PORT": _check_port(port) if port else None,
    }
