"""Chargement et contrôle de `config/rules.toml` et de `.env`.

Chaque erreur est une `ConfigError` à message unique par cause : elle nomme le
fichier, la ligne quand elle est connue, la clé et la valeur reçue. La valeur
d'un secret n'apparaît jamais dans un message.
"""

import hashlib
import math
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
IA_RATES = ("louis", "mixte", "ia")
PORTS = range(1024, 65536)
MAX_INT_DIGITS = 4300
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
TOML_LINE_PATTERN = re.compile(r"at line (\d+)")


class ConfigError(Exception):
    """Configuration illisible ou invalide."""


def _read_bytes(path, missing_hint=""):
    """Lit un fichier de configuration, ou lève une erreur qui nomme le chemin."""
    path = Path(path)
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise ConfigError(f"{path} : fichier absent{missing_hint}") from None
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
        self.lines = text.split("\n")
        self.data = data

    def fail(self, section, key, problem, value=None):
        """Lève l'erreur avec fichier, ligne, clé et valeur reçue."""
        number = _locate(self.lines, section, key)
        where = f"{self.path}:{number}" if number else str(self.path)
        message = f"{where} : clé `{section}.{key}` {problem}"
        if value is not None:
            message += f" (valeur reçue : {value!r})"
        raise ConfigError(message)

    def table(self, name, allow_empty=False):
        """Renvoie la famille `name` : une table, non vide sauf `allow_empty`."""
        value = self.data.get(name)
        if value is None:
            raise ConfigError(f"{self.path} : famille `{name}` absente")
        if not isinstance(value, dict):
            raise ConfigError(
                f"{self.path} : famille `{name}` mal typée (valeur reçue : {value!r})"
            )
        if not value and not allow_empty:
            raise ConfigError(f"{self.path} : famille `{name}` vide")
        return value

    def value(self, section, key, table):
        """Renvoie `table[key]`, qui doit exister."""
        if key not in table:
            self.fail(section, key, "est absente")
        return table[key]

    def text(self, section, key, table):
        """Renvoie le texte non vide `table[key]`."""
        value = self.value(section, key, table)
        if not isinstance(value, str):
            self.fail(section, key, "doit être un texte", value)
        if not value.strip():
            self.fail(section, key, "est vide", value)
        return value

    def number(self, section, key, table):
        """Renvoie le nombre fini `table[key]`."""
        value = self.value(section, key, table)
        if type(value) not in (int, float):
            self.fail(section, key, "doit être un nombre", value)
        if  isinstance(value, float) \
            and not math.isfinite(value):
            self.fail(section, key, "doit être un nombre fini", value)
        return value

    def texts(self, section, key, value):
        """Renvoie `value` s'il s'agit d'une liste de textes."""
        if not isinstance(value, list):
            self.fail(section, key, "doit être une liste de textes", value)
        for item in value:
            if not isinstance(item, str):
                self.fail(section, key, "ne doit contenir que des textes", item)
        return value

    def check_states(self):
        states = self.table("states", allow_empty=True)
        order = self.texts("states", "order", self.value("states", "order", states))
        if not order:
            self.fail("states", "order", "est vide", order)
        seen = set()
        for state in order:
            if state in seen:
                self.fail("states", "order", "contient un état en double", state)
            seen.add(state)
        for state in self.texts("states", "excluded", states.get("excluded", [])):
            if state not in seen:
                self.fail("states", "excluded", "nomme un état hors de `order`", state)
        self.check_cert_ready(states, order)

    def check_cert_ready(self, states, order):
        """Contrôle `cert_ready_at_least` : un état de `order` non exclu."""
        state = self.text("states", "cert_ready_at_least", states)
        if state in states.get("excluded", []):
            self.fail("states", "cert_ready_at_least", "nomme un état exclu", state)
        if state not in order:
            allowed = ", ".join(order)
            problem = f"doit nommer un état de `states.order` ({allowed})"
            self.fail("states", "cert_ready_at_least", problem, state)

    def check_typed(self, family):
        """Chaque rang ou titre est une table avec un `type` textuel."""
        for name, entry in self.table(family).items():
            if not isinstance(entry, dict):
                self.fail(family, name, "doit être une table", entry)
            self.text(f"{family}.{name}", "type", entry)

    def check_titles(self):
        """Un titre qui porte un `rank` nomme une clé de `ranks`."""
        self.check_typed("titles")
        for name, entry in self.data["titles"].items():
            if "rank" not in entry:
                continue
            rank = self.text(f"titles.{name}", "rank", entry)
            if rank not in self.data["ranks"]:
                self.fail(f"titles.{name}", "rank", "doit nommer un rang de `ranks`", rank)

    def check_ia(self):
        ia = self.table("ia")
        for name in IA_RATES:
            rate = self.number("ia", name, ia)
            if not 0 <= rate <= 1:
                self.fail("ia", name, "doit être un taux entre 0 et 1", rate)

    def check_xp_table(self):
        table = self.table("xp_table")
        url = self.text("xp_table", "url", table)
        commit = self.text("xp_table", "commit", table)
        sha256 = self.text("xp_table", "sha256", table)
        if not url.startswith("https://"):
            self.fail("xp_table", "url", "doit commencer par `https://`", url)
        if not COMMIT_PATTERN.fullmatch(commit):
            self.fail("xp_table", "commit", "doit avoir 40 hexadécimaux", commit)
        if commit not in url:
            self.fail("xp_table", "url", "doit contenir le commit épinglé", url)
        if not SHA256_PATTERN.fullmatch(sha256):
            self.fail("xp_table", "sha256", "doit avoir 64 hexadécimaux", sha256)

    def check_calibration(self):
        calibration = self.table("calibration")
        for key in ("target_level", "min_projects", "min_days"):
            value = self.value("calibration", key, calibration)
            if type(value) is not int:
                self.fail("calibration", key, "doit être un entier", value)
            if value < 1:
                self.fail("calibration", key, "doit être positif", value)
        initial = self.number("calibration", "r_initial", calibration)
        if initial < 0:
            self.fail("calibration", "r_initial", "ne peut pas être négatif", initial)


def _toml_error(path, error):
    """Renvoie une `ConfigError` française, avec `chemin:ligne` quand la ligne est connue."""
    found = TOML_LINE_PATTERN.search(str(error))
    where = f"{path}:{found.group(1)}" if found else str(path)
    return ConfigError(f"{where} : syntaxe TOML invalide")


def load_rules(path):
    """Charge `rules.toml`, le valide et renvoie le dictionnaire des six familles.

    Args:
        path: chemin du fichier de règles.

    Returns:
        dict : états, rangs, taux d'IA, table XP, calibration et titres.

    Raises:
        ConfigError: fichier absent, vide, non UTF-8 ou mal formé, ou règle
            invalide (une cause par message, valeur reçue citée).
    """
    path = Path(path)
    text = _decode(path, _read_bytes(path))
    if not text.strip():
        raise ConfigError(f"{path} : fichier vide")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise _toml_error(path, error) from None
    rules = _Rules(path, text, data)
    rules.check_states()
    rules.check_typed("ranks")
    rules.check_titles()
    rules.check_ia()
    rules.check_calibration()
    rules.check_xp_table()
    return data


def _unquote(value, where):
    """Retire une paire de guillemets simples ou doubles autour d'une valeur."""
    if value[:1] not in ("\"", "'"):
        return value
    if len(value) < 2 or value[-1] != value[0]:
        raise ConfigError(f"{where} : guillemet non fermé")
    return value[1:-1]


def load_env(path):
    """Lit un fichier `.env` : une variable connue par ligne, `CLE=valeur`.

    Les lignes vides et les commentaires `#` en début de ligne sont permis. Une
    valeur garde tout ce qui suit `=`, `#` compris, et perd ses guillemets.

    Args:
        path: chemin du fichier `.env`.

    Returns:
        dict[str, str] : variable, valeur non contrôlée.

    Raises:
        ConfigError: fichier absent ou illisible, ligne sans `=`, clé vide,
            guillemet non fermé, variable inconnue ou en doublon.
    """
    path = Path(path)
    hint = f" ; variables attendues : {', '.join(ENV_VARIABLES)}"
    text = _decode(path, _read_bytes(path, hint)).replace("\r", "")
    env = {}
    first_seen = {}
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped or stripped[0] == "#":
            continue
        where = f"{path}:{number}"
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator:
            raise ConfigError(f"{where} : ligne sans `=`, `CLE=valeur` attendu")
        if not key:
            raise ConfigError(f"{where} : clé vide avant `=`")
        if key not in ENV_VARIABLES:
            raise ConfigError(f"{where} : variable inconnue `{key}`")
        if key in env:
            raise ConfigError(
                f"{where} : clé `{key}` en doublon (déjà définie ligne {first_seen[key]})"
            )
        env[key] = _unquote(value.strip(), where)
        first_seen[key] = number
    return env


def _check_port(text):
    """Convertit strictement le port, ou lève une erreur qui cite la valeur."""
    is_integer = re.fullmatch(f"[0-9]{{1,{MAX_INT_DIGITS}}}", text)
    port = int(text) if is_integer else None
    if port not in PORTS:
        raise ConfigError(
            f"API42_CALLBACK_PORT : port invalide, entier de {PORTS.start} à {PORTS[-1]} "
            f"attendu (valeur reçue : {text})"
        )
    return port


def _resolve(name, text):
    """Développe `~` et rend le chemin absolu depuis le dossier courant."""
    try:
        return Path(text).expanduser().absolute()
    except RuntimeError:
        raise ConfigError(
            f"{name} : dossier personnel introuvable (valeur reçue : {text})"
        ) from None
    except OSError as error:
        raise ConfigError(f"{name} : dossier courant illisible ({error.strerror})") from None


def _check_suivi_dir(text):
    """Le dossier du suivi doit exister et être un dossier."""
    path = _resolve("PROFESSOR_SUIVI_DIR", text)
    try:
        exists = path.exists()
        is_dir = path.is_dir()
    except OSError as error:
        raise ConfigError(
            f"PROFESSOR_SUIVI_DIR : chemin inaccessible ({path}, {error.strerror})"
        ) from None
    if not exists:
        raise ConfigError(f"PROFESSOR_SUIVI_DIR : chemin inexistant ({path})")
    if not is_dir:
        raise ConfigError(f"PROFESSOR_SUIVI_DIR : fichier au lieu d'un dossier ({path})")
    return path


def check_env(env):
    """Contrôle et convertit les variables lues par `load_env`.

    Les deux chemins sont obligatoires, le dossier du suivi doit exister et un
    chemin relatif part du dossier courant. Un port vide donne `None`.

    Args:
        env: dict[str, str] des cinq variables, valeurs non contrôlées.

    Returns:
        dict : les deux chemins en `Path` absolu, identifiant et secret en
        texte, port en `int` de 1024 à 65535 ou `None`.

    Raises:
        ConfigError: variable obligatoire vide, chemin ou port invalide.
    """
    for name in REQUIRED_PATHS:
        if not env.get(name, "").strip():
            raise ConfigError(f"{name} : variable obligatoire absente ou vide")
    port = env.get("API42_CALLBACK_PORT", "").strip()
    return {
        "PROFESSOR_SUIVI_DIR": _check_suivi_dir(env["PROFESSOR_SUIVI_DIR"].strip()),
        "IA_HISTORY_CSV": _resolve("IA_HISTORY_CSV", env["IA_HISTORY_CSV"].strip()),
        "API42_CLIENT_ID": env.get("API42_CLIENT_ID", ""),
        "API42_CLIENT_SECRET": env.get("API42_CLIENT_SECRET", ""),
        "API42_CALLBACK_PORT": _check_port(port) if port else None,
    }
