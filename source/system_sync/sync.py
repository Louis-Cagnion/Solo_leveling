"""Commande `sync` (T10) : lit `/professor` et l'API 42, applique les règles, écrit l'état.

Ordre : règles, `.env`, dossier de sortie, six sources de `/professor`, API 42, table XP,
construction de l'état, écriture atomique validée (`output.write`), puis ligne de
trajectoire. Le cache de l'API 42 (`cache/api42.json`), celui de la table XP
(`cache/xp_table.json`) et la trajectoire (`history/trajectory.jsonl`) vivent dans le
dossier de la sortie. Le journal (horodatage, niveau) va sur l'erreur standard, avec le
secret et les chemins des caches masqués. Contrat : `tests/system_sync/test_sync.py`.
"""

import argparse
import contextlib
import json
import logging
import math
import re
import sys
import unicodedata
import webbrowser
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from system_sync import output
from system_sync.config import (
    ConfigError,
    check_env,
    load_env,
    load_rules,
    rules_fingerprint,
)
from system_sync.model import Anomaly, StatedValue, observed, unmeasurable
from system_sync.rules import calibration, network, ranks, titles
from system_sync.rules import xp as xp_rules
from system_sync.sources import api42, professor, xp_table

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULES = ROOT / "config" / "rules.toml"
DEFAULT_OUTPUT = ROOT / "data" / "state.js"
PROG = "python3 -m system_sync sync"
LOGGER = logging.getLogger(__name__)
LOG_ROOT = "system_sync"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MASK = "<masqué>"
INTERRUPTED = 130
TRAJECTORY_FILE = "trajectory.jsonl"
TRAJECTORY_KEYS = frozenset({"date", "level42", "system_level"})
# Options de `sync` : nom, puis arguments de `ArgumentParser.add_argument`.
OPTIONS = {
    "--env": {
        "type": Path,
        "default": ROOT / ".env",
        "metavar": "CHEMIN",
        "help": "fichier .env (défaut : .env à la racine du dépôt)",
    },
    "--sortie": {
        "type": Path,
        "default": DEFAULT_OUTPUT,
        "metavar": "CHEMIN",
        "help": "fichier state.js à écrire (défaut : data/state.js du dépôt)",
    },
}
# Portée, condition (texte à trous des clés du titre) et cible de chaque type de titre.
TITLE_SCOPES = {"level_at_least": "42", "rank_on_all_cards": "Système"}
TITLE_CONDITIONS = {
    "level_at_least": "niveau 42 au moins égal à {value}",
    "rank_on_all_cards": "rang {rank} sur toutes les cartes",
}


@dataclass(frozen=True)
class _Run:
    """Paramètres d'un lancement : fichiers et points d'injection des tests."""

    env_file: Path
    output: Path
    rules_path: Path
    open_browser: object
    api_base: str
    xp_loader: object

    @property
    def cache_dir(self):
        return self.output.parent / "cache"

    @property
    def trajectory_file(self):
        return self.output.parent / "history" / TRAJECTORY_FILE


@dataclass(frozen=True)
class _Inputs:
    """Tout ce que lit une synchronisation, prêt pour la construction de l'état."""

    rules: dict
    fingerprint: str
    found: dict
    api: object
    table: object
    now: datetime
    trajectory: tuple
    trajectory_anomalies: tuple

    @property
    def day(self):
        return self.now.date()


class _Redactor(logging.Filter):
    """Filtre de journal qui masque les textes à ne jamais écrire (secret, caches)."""

    def __init__(self):
        super().__init__()
        self.hidden = []

    def hide(self, *texts):
        """Ajoute des textes à masquer, les vides étant ignorés."""
        self.hidden.extend(str(text) for text in texts if str(text))

    def filter(self, record):
        text = record.getMessage()
        for hidden in self.hidden:
            text = text.replace(hidden, MASK)
        record.msg, record.args = text, None
        return True


@contextlib.contextmanager
def _journal():
    """Branche le journal horodaté sur l'erreur standard le temps d'un lancement.

    Yields:
        Le `_Redactor` du gestionnaire, pour y déclarer les textes à masquer.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    redactor = _Redactor()
    handler.addFilter(redactor)
    logger = logging.getLogger(LOG_ROOT)
    saved = (logger.level, logger.propagate)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        yield redactor
    finally:
        logger.removeHandler(handler)
        logger.setLevel(saved[0])
        logger.propagate = saved[1]


def _plain(value):
    """Rend la forme JSON d'une valeur : valeurs statuées, anomalies, tuples et dicts."""
    if isinstance(value, (StatedValue, Anomaly)):
        return value.to_dict()
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _slug(name):
    """Identifiant d'une carte : son nom en minuscules sans accent, séparé par des tirets."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "card"


def _parse(argv):
    """Analyse les options de `sync` ; `argparse` quitte par `SystemExit` si invalides."""
    parser = argparse.ArgumentParser(prog=PROG, description="Synchronise l'état du Système.")
    for name, settings in OPTIONS.items():
        parser.add_argument(name, **settings)
    return parser.parse_args(argv)


def _log_source(result):
    """Journalise le statut et les volumes d'une source de `/professor`."""
    level = logging.WARNING if result.status == "unavailable" else logging.INFO
    LOGGER.log(
        level,
        "source %s : %s, %d lignes lues, %d rejetées, %d anomalies",
        result.name,
        result.status,
        result.read,
        result.rejected,
        len(result.anomalies),
    )
    if result.error:
        LOGGER.warning("source %s : %s", result.name, result.error)


def _read_professor(env):
    found = professor.read_professor(env["PROFESSOR_SUIVI_DIR"], env["IA_HISTORY_CSV"])
    for result in found.values():
        _log_source(result)
    return found


def _read_api(run, env):
    """Lit l'API 42 (consentement, repli sur le cache) ; son `error` n'est pas journalisé."""
    result = api42.read_api42(
        env,
        run.cache_dir / "api42.json",
        open_browser=run.open_browser,
        api_base=run.api_base,
    )
    LOGGER.info(
        "source api42 : %s, %d éléments lus, %d rejetés, %d anomalies",
        result.status,
        result.read,
        result.rejected,
        len(result.anomalies),
    )
    return result


def _read_table(run, rules):
    """Charge la table XP épinglée ; une erreur d'un résultat `ok` est un avertissement."""
    pinned = rules["xp_table"]
    result = run.xp_loader(
        pinned["url"],
        pinned["commit"],
        pinned["sha256"],
        run.cache_dir / "xp_table.json",
    )
    LOGGER.info("table XP : %s", result.status)
    if result.error:
        LOGGER.warning("table XP : %s", result.error)
    return result


def _trajectory_line(text):
    """Renvoie la ligne de trajectoire lue, ou la cause pour laquelle elle est refusée."""
    try:
        line = json.loads(text)
    except ValueError:
        return None, "JSON illisible"
    if not isinstance(line, dict) or set(line) != TRAJECTORY_KEYS:
        return None, "clés attendues : date, level42, system_level"
    try:
        date.fromisoformat(line["date"])
    except (TypeError, ValueError):
        return None, f"date {line['date']!r} illisible"
    for key in ("level42", "system_level"):
        number = line[key]
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            return None, f"{key} : nombre attendu"
        if not math.isfinite(number) or number < 0:
            return None, f"{key} : nombre fini positif ou nul attendu"
    return line, None


def _read_trajectory(path):
    """Lit les lignes de trajectoire ; une ligne refusée devient une anomalie.

    Returns:
        Couple (tuple des lignes valides, tuple d'`Anomaly`).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return (), ()
    except (OSError, UnicodeDecodeError) as error:
        cause = getattr(error, "strerror", None) or "octets non UTF-8"
        raise OSError(f"{path} : lecture impossible ({cause})") from None
    lines, anomalies = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        line, cause = _trajectory_line(raw)
        if line is None:
            anomalies.append(Anomaly(path.name, number, "malformed_trajectory", cause))
        else:
            lines.append(line)
    LOGGER.info("trajectoire : %d lignes lues, %d rejetées", len(lines), len(anomalies))
    return tuple(lines), tuple(anomalies)


def _append_trajectory(path, lines):
    """Ajoute des lignes JSON en fin de fichier de trajectoire, dossier créé au besoin."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line) + "\n")


def _facts(found):
    events = found["events"]
    return events.facts if events.status == "ok" else None


def _placement(cards):
    """Associe chaque identifiant de notion à (identifiant de carte, palier en minuscules)."""
    return {
        note_id: (_slug(card["name"]), tier.lower())
        for card in cards
        for tier, ids in card["tiers"].items()
        for note_id in ids
    }


def _notion_entry(note_id, note, placement, lowest):
    """Entrée de `notions{}` ; sans ligne dans `notions.md`, la notion est au plus bas état."""
    card, tier = placement.get(note_id, (None, None))
    return {
        "label": note.get("title", note_id),
        "section": note.get("section"),
        "state": observed(note.get("state", lowest), ("notions",)),
        "goal": note.get("objective") or None,
        "card": card,
        "tier": tier,
        "last_practice": note.get("last_practice"),
    }


def _notions_entity(notions, cards, rules):
    """Notions de `notions.md`, puis celles que seules les cartes citent."""
    placement = _placement(cards)
    known = {note["id"]: note for note in notions}
    lowest = rules["states"]["order"][0]
    ids = [*known, *(note_id for note_id in placement if note_id not in known)]
    return {
        note_id: _notion_entry(note_id, known.get(note_id, {}), placement, lowest)
        for note_id in ids
    }


def _card_entity(card, inputs, notions, cards):
    """Construit une carte ; le rang suivant n'est lu que si le rang est mesuré."""
    rules, facts = inputs.rules, _facts(inputs.found)
    rank = ranks.rank_card(card, notions, facts, rules)
    following = None
    if rank.status != "unmeasurable":
        following = ranks.next_rank(card, notions, facts, rules)
    return {
        "id": _slug(card["name"]),
        "name": card["name"],
        "rank": rank,
        "next_rank": following,
        "tiers": [
            {"name": tier.lower(), "notions": list(ids)}
            for tier, ids in card["tiers"].items()
        ],
        "certifications": ranks.card_certifications(card, cards, notions, facts, rules),
    }


def _relations_entity(kept):
    return [
        {
            "source": relation["source"],
            "target": relation["target"],
            "kind": relation["relation"],
            "status": relation["status"],
            "limit": relation["limit"] or None,
            "proof": relation["proof"] or None,
        }
        for relation in kept
    ]


def _title_progress(obtained, progress):
    """Valeur statuée de progression : le courant du titre, ou la raison de l'absence."""
    if progress is not None:
        return StatedValue(progress["current"], obtained.status, obtained.sources)
    if obtained.status == "unmeasurable":
        return obtained
    return unmeasurable("progression non mesurable", "card_unmeasurable")


def _titles_entity(inputs, level, card_ranks):
    configured = inputs.rules["titles"]
    found = titles.school_titles(level, card_ranks, _facts(inputs.found), inputs.rules)
    entity = []
    for item in found:
        spec = configured[item["id"]]
        progress = item["progress"]
        entity.append(
            {
                "id": item["id"],
                "name": item.get("name", item["id"]),
                "scope": TITLE_SCOPES[item["type"]],
                "condition": TITLE_CONDITIONS[item["type"]].format(**spec),
                "obtained": item["obtained"],
                "progress": _title_progress(item["obtained"], progress),
                "target": None if progress is None else progress["target"],
            }
        )
    return entity


def _achievements_entity(api):
    """Entité `achievements` du schéma : liste complète et éléments aux identifiants texte."""
    entity = titles.achievements_entity(api.achievements, api.complete)
    return {
        "complete": entity["complete"],
        "items": [{**item, "id": str(item["id"])} for item in entity["items"]],
    }


def _validated(api):
    """Projets 42 validés, ou `None` si l'API n'a rien donné (ni lecture ni cache)."""
    return None if api.status == "unavailable" else api.projects


def _project_inputs(found):
    """Renvoie (projets, historique) pour les règles : `None` si la source manque.

    Un échec de lecture de `projets.csv` donne `()` et non `None` (A5).
    """
    projects, history = found["projects"], found["history"]
    return (
        None if projects.status == "absent" else projects.records,
        history.records if history.status == "ok" else None,
    )


def _rules_entity(rules):
    states = rules["states"]
    order = [name for name in states["order"][1:] if name not in states["excluded"]]
    return {
        "proof_order": order,
        "excluded_states": list(states["excluded"]),
        "rank_d_threshold": _rule(rules, "ranks", "D", "fallback_at_least"),
        "cert_threshold": states["cert_ready_at_least"],
        "target_level": rules["calibration"]["target_level"],
    }


def _rule(rules, *keys):
    """Renvoie une règle imbriquée, ou lève une `ConfigError` qui la nomme."""
    value = rules
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise ConfigError(f"règles : clé `{'.'.join(keys)}` absente")
        value = value[key]
    return value


def _sources_entity(inputs):
    entity = [
        {
            "name": name,
            "status": result.status,
            "lines_read": result.read,
            "lines_rejected": result.rejected,
            "observed_at": None,
        }
        for name, result in inputs.found.items()
    ]
    api = inputs.api
    entity.append(
        {
            "name": "api42",
            "status": api.status,
            "lines_read": api.read,
            "lines_rejected": api.rejected,
            "observed_at": api.observed_at,
        }
    )
    return entity


def _anomalies(inputs):
    """Rassemble sans doublon les anomalies des sources et des règles, dans l'ordre."""
    found, api, rules = inputs.found, inputs.api, inputs.rules
    cards, notions = found["cards"].records, found["notions"].records
    relations = found["relations"].records
    projects, history = _project_inputs(found)
    facts = _facts(found)
    groups = [
        *(result.anomalies for result in found.values()),
        api.anomalies,
        inputs.trajectory_anomalies,
        ranks.rank_anomalies(cards, notions, facts, rules),
        network.network_anomalies(relations, notions, cards, rules),
        titles.title_anomalies(facts, rules),
        xp_rules.project_anomalies(
            projects,
            history,
            None,
            _validated(api),
            rules,
            inputs.day,
        ),
        titles.achievement_anomalies(api.achievements, api.complete),
    ]
    return tuple(dict.fromkeys(anomaly for group in groups for anomaly in group))


def _level42(inputs):
    """Entité `level42` : niveau de l'API, XP et XP cible de la table, projets validés."""
    api, table = inputs.api, inputs.table
    target = inputs.rules["calibration"]["target_level"]
    return xp_rules.level42_entity(
        api.level,
        xp_table.xp_for_level(table, api.level.value),
        xp_table.xp_for_level(table, target),
        _validated(api),
        None,
    )


def _system(inputs, level42):
    """Renvoie (entité `system`, projets perso et pro) : XP, niveau calibré, origines."""
    rules, found = inputs.rules, inputs.found
    projects, history = _project_inputs(found)
    entries = xp_rules.project_entries(
        projects,
        history,
        None,
        _validated(inputs.api),
        rules,
        inputs.day,
    )
    absent = found["projects"].status == "absent"
    system = xp_rules.system_xp(level42["xp"], None if absent else entries)
    levels = inputs.table.table.levels if inputs.table.table else None
    calibrated = calibration.calibrate(
        system["xp"],
        level42["xp"],
        None if absent else entries,
        rules["calibration"].get("anchors"),
        levels,
        rules,
        inputs.day,
    )
    entity = {**system, "level": calibrated["level"], "calibration": calibrated["calibration"]}
    return entity, entries


def _build_state(inputs):
    """Assemble les 14 entités de l'état, avant sérialisation.

    Returns:
        Couple (état, lignes de trajectoire nouvelles à enregistrer après l'écriture).
    """
    found, api, rules = inputs.found, inputs.api, inputs.rules
    cards, notions = found["cards"].records, found["notions"].records
    kept, _ = network.control_relations(found["relations"].records, notions, cards)
    level42 = _level42(inputs)
    system, entries = _system(inputs, level42)
    card_entities = [_card_entity(card, inputs, notions, cards) for card in cards]
    card_ranks = {card["name"]: entity["rank"] for card, entity in zip(cards, card_entities)}
    trajectory = calibration.extend_trajectory(
        inputs.trajectory,
        inputs.day,
        level42["level"],
        system["level"],
    )
    achievements = _achievements_entity(api)
    state = {
        "meta": {
            "schema_version": 1,
            "generated_at": inputs.now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rules_fingerprint": inputs.fingerprint,
        },
        "sources": _sources_entity(inputs),
        "level42": level42,
        "system": system,
        "trajectory": trajectory,
        "cards": card_entities,
        "notions": _notions_entity(notions, cards, rules),
        "relations": _relations_entity(kept),
        "projects": entries,
        "titles": _titles_entity(inputs, level42["level"], card_ranks),
        "anomalies": _anomalies(inputs),
        "rules": _rules_entity(rules),
        "achievements": achievements,
        "names": {"en": {}},
    }
    return _plain(state), trajectory[len(inputs.trajectory):]


def _prepare_output(run):
    """Crée le dossier de sortie avant toute lecture ; False (et journal) si impossible."""
    try:
        run.output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        LOGGER.error("%s : %s", run.output.parent, error.strerror or error)
        return False
    return True


def _synchronise(run, redactor):
    """Déroule une synchronisation complète ; rend le code de sortie."""
    rules = load_rules(run.rules_path)
    fingerprint = rules_fingerprint(run.rules_path)
    LOGGER.info("règles : %s chargées, empreinte %s", run.rules_path, fingerprint)
    env = check_env(load_env(run.env_file))
    redactor.hide(
        env["API42_CLIENT_SECRET"],
        run.cache_dir / "api42.json",
        run.cache_dir / "xp_table.json",
    )
    if not _prepare_output(run):
        return 1
    found = _read_professor(env)
    api = _read_api(run, env)
    table = _read_table(run, rules)
    trajectory, malformed = _read_trajectory(run.trajectory_file)
    inputs = _Inputs(
        rules,
        fingerprint,
        found,
        api,
        table,
        datetime.now(timezone.utc),
        trajectory,
        malformed,
    )
    state, new_lines = _build_state(inputs)
    output.write(state, run.output)
    LOGGER.info("état écrit dans %s (%d anomalies)", run.output, len(state["anomalies"]))
    _append_trajectory(run.trajectory_file, new_lines)
    LOGGER.info("trajectoire : %d ligne(s) ajoutée(s)", len(new_lines))
    return 0


def run_sync(
    argv,
    *,
    open_browser=None,
    api_base=None,
    rules_path=None,
    xp_loader=None,
):
    """Lance une synchronisation.

    Args:
        argv: options après `sync` (`--env`, `--sortie`), liste de textes.
        open_browser: fonction URL vers booléen ; `None` pour `webbrowser.open`.
        api_base: base de l'API 42 ; `None` pour l'API réelle.
        rules_path: chemin de `rules.toml` ; `None` pour celui du dépôt.
        xp_loader: de la signature de `xp_table.load_xp_table` ; `None` pour elle.

    Returns:
        0 si l'état est écrit ; 2 pour une option inconnue ; 130 si interrompue ;
        1 pour une erreur de configuration, de règles ou d'écriture.
    """
    try:
        options = _parse(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 2
    run = _Run(
        options.env,
        options.sortie.absolute(),
        Path(rules_path) if rules_path else DEFAULT_RULES,
        open_browser or webbrowser.open,
        api_base or api42.API_BASE,
        xp_loader or xp_table.load_xp_table,
    )
    with _journal() as redactor:
        try:
            return _synchronise(run, redactor)
        except (ConfigError, output.OutputError, OSError) as error:
            LOGGER.error("synchronisation interrompue : %s", error)
        except KeyboardInterrupt:
            LOGGER.error("synchronisation interrompue par l'utilisateur")
            return INTERRUPTED
    return 1
