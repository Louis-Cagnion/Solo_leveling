"""XP du niveau 42 et XP Système (T7, A4 à A6, A17, A18) : fonctions pures, sans source.

Les données arrivent lues : `projets.csv` et `historique-ia.csv` par `sources/professor`,
le catalogue des projets 42 (A4) et les projets validés par leurs sources. Le facteur d'IA
d'un projet est la moyenne des taux `rules["ia"]` de ses lignes d'historique, `lecture`
exclue (`c:148`) ; son XP est la base de son équivalent 42 multipliée par ce facteur. Aucune
fonction publique ne lève : une donnée inutilisable donne une valeur `unmeasurable`, `()`
ou une entité aux mêmes clés. Contrat : `tests/system_sync/rules/test_xp.py`.
"""

import math
from dataclasses import dataclass
from datetime import date

from system_sync.model import Anomaly, StatedValue, estimated, insufficient, unmeasurable
from system_sync.output import PROJECT_SETTINGS, PROJECT_STATUSES
from system_sync.rules.guard import empty, never_raises

PROJECTS_FILE = "projets.csv"
HISTORY_FILE = "historique-ia.csv"
API_SOURCE = "api42"
PROJECTS_SOURCE = "projects"
HISTORY_SOURCE = "history"
CATALOGUE_SOURCE = "catalogue_42"
READING_AUTHOR = "lecture"
PERSONAL = "perso"
DELIVERED = "livré"
ESTIMATED = "estimated"
# Statuts d'une valeur qui porte une mesure exploitable.
MEASURED = ("observed", ESTIMATED)
# Origines de l'XP Système, dans l'ordre de `system.origins`.
ORIGINS = ("42", *PROJECT_SETTINGS)
# Plus ancienne date de projet plausible (fiche T7, cas L8).
EARLIEST_DATE = date(2020, 1, 1)
# Ajouté avant `math.floor` : arrondi à l'entier, moitié vers le haut (A6).
HALF = 0.5
NO_PROJECT = "aucun projet perso ou pro enregistré"
NO_PROJECT_CODE = "no_personal_project"
API_CODE = "api_unavailable"
XP_INVALID_CODE = "xp_invalid"
UNKNOWN_CODE = "equivalent_unknown"
AMBIGUOUS_CODE = "ambiguous_project_key"
NO_HISTORY_CODE = "ia_history_missing"
THIRD_PARTY_CODE = "third_party_table"


@dataclass(frozen=True)
class _Context:
    """Données communes au calcul de chaque projet.

    Args:
        groups: lignes d'historique de `_spellings`, ou `None` sans historique.
        rates: dict auteur vers taux de `rules["ia"]`.
        bases: dict `slug` vers `difficulty` de `_bases`, ou `None` sans catalogue.
        validated: ensemble des `slug` des projets 42 validés.
        today: `datetime.date` de la synchronisation.
    """

    groups: object
    rates: dict
    bases: object
    validated: frozenset
    today: date


def is_number(value):
    """Dit si `value` est un nombre non booléen, fini et représentable en flottant."""
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
    ):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def is_nonnegative(value):
    """Dit si `value` est un nombre fini, non booléen et positif ou nul."""
    return (
        is_number(value)
        and value >= 0
    )


def _is_text(value):
    """Dit si `value` est un texte non vide."""
    return (
        isinstance(value, str)
        and bool(value.strip())
    )


def missing_measure(state, noun, invalid_code):
    """Renvoie la valeur `unmeasurable` d'une mesure inutilisable, ou `None` si elle sert.

    Args:
        state: valeur statuée attendue (niveau, XP), ou toute autre valeur reçue.
        noun: nom de la mesure dans la raison, texte.
        invalid_code: code de `REASON_CODES` d'une valeur qui n'est pas un nombre fini.

    Returns:
        `None` pour une valeur observée ou estimée de nombre fini ; sinon une valeur
        `unmeasurable` qui reprend la raison et le code reçus (`api_unavailable` sans
        valeur statuée, `invalid_code` pour un nombre inutilisable).
    """
    if not isinstance(state, StatedValue):
        reason = f"{noun} : valeur reçue {state!r}, API 42 indisponible"
        return unmeasurable(reason, API_CODE)
    if state.status not in MEASURED:
        return unmeasurable(state.reason, state.reason_code)
    if not is_number(state.value):
        return unmeasurable(f"{noun} {state.value!r} : nombre fini attendu", invalid_code)
    return None


def _without_value(state):
    """Reprend le statut, la raison et le code d'une valeur non estimée, sans valeur."""
    return StatedValue(None, state.status, (), state.reason, state.reason_code)


def _record_problem(record):
    """Renvoie la cause pour laquelle un enregistrement de `projets.csv` est mal formé.

    Args:
        record: dict de `read_projects(...).records`.

    Returns:
        Le détail qui nomme la valeur reçue, ou `None` si l'enregistrement est utilisable.
    """
    project_id, frame = record.get("id"), record.get("frame")
    status, equivalent = record.get("status"), record.get("equivalent_42")
    if not _is_text(project_id):
        return f"id {project_id!r} vide ou non texte"
    if frame not in PROJECT_SETTINGS:
        return f"cadre {frame!r} hors de {PROJECT_SETTINGS}"
    if status not in PROJECT_STATUSES:
        return f"statut {status!r} hors de {PROJECT_STATUSES}"
    if not _is_text(equivalent):
        return f"equivalent_42 {equivalent!r} absent ou vide"
    return None


def _scan(projects):
    """Classe les enregistrements de `projets.csv` : gardé, mal formé ou en doublon.

    Args:
        projects: liste ou tuple de dicts de `read_projects`, ou toute autre valeur.

    Returns:
        Une liste de (enregistrement, nature, détail) dans l'ordre reçu ; la nature est
        `None` pour un enregistrement gardé, sinon `malformed_project` ou
        `duplicate_project` (même `id` sans tenir compte de la casse, le premier gardé).
    """
    if not isinstance(projects, (list, tuple)):
        return []
    first_lines, scanned = {}, []
    for record in projects:
        problem = _record_problem(record)
        if problem is not None:
            scanned.append((record, "malformed_project", problem))
            continue
        key = record["id"].casefold()
        if key in first_lines:
            detail = f"id {record['id']!r} déjà lu ligne {first_lines[key]} : doublon ignoré"
            scanned.append((record, "duplicate_project", detail))
        else:
            first_lines[key] = record.get("line")
            scanned.append((record, None, None))
    return scanned


def _kept(projects):
    """Renvoie les enregistrements utilisables de `projets.csv`, sans doublon."""
    return [record for record, kind, _ in _scan(projects) if kind is None]


def _spellings(history):
    """Regroupe les lignes d'historique par projet sans tenir compte de la casse (A5).

    Args:
        history: liste ou tuple de dicts de `read_history`, ou toute autre valeur.

    Returns:
        Un dict clé sans casse vers dict graphie vers lignes, dans l'ordre reçu ;
        `None` si `history` n'est pas une liste.
    """
    if not isinstance(history, (list, tuple)):
        return None
    groups = {}
    for line in history:
        spelling = line["project"]
        groups.setdefault(spelling.casefold(), {}).setdefault(spelling, []).append(line)
    return groups


def _rates(rules):
    """Renvoie la table `rules["ia"]` (auteur vers taux) ; `TypeError` si non dict."""
    rates = rules["ia"]
    if not isinstance(rates, dict):
        raise TypeError(f"rules[ia] {rates!r} : table attendue")
    return rates


def _ambiguity(project_id, spellings):
    """Décrit une clé de projet écrite de plusieurs façons dans l'historique (`c:94`)."""
    written = ", ".join(repr(spelling) for spelling in spellings)
    return f"projet {project_id!r} écrit {written} dans {HISTORY_FILE} : clé ambiguë"


def _ia_factor(project_id, groups, rates):
    """Calcule le facteur d'IA d'un projet : moyenne des taux de ses lignes notées.

    Args:
        project_id: `id` du projet, texte.
        groups: lignes d'historique de `_spellings`, ou `None` sans historique.
        rates: dict auteur vers taux de `rules["ia"]`.

    Returns:
        La valeur `estimated` (code `ia_rate`) ; `unmeasurable` sans ligne ou sans
        historique ; `insufficient` pour une clé ambiguë ou sans ligne notée.
    """
    if groups is None:
        reason = f"{HISTORY_FILE} absent ou illisible : facteur d'IA de {project_id!r} inconnu"
        return unmeasurable(reason, NO_HISTORY_CODE)
    spellings = groups.get(project_id.casefold(), {})
    if not spellings:
        reason = f"projet {project_id!r} sans ligne dans {HISTORY_FILE}"
        return unmeasurable(reason, NO_HISTORY_CODE)
    if len(spellings) > 1:
        return insufficient(_ambiguity(project_id, spellings), AMBIGUOUS_CODE)
    lines = next(iter(spellings.values()))
    rated = [rates[line["author"]] for line in lines if line["author"] in rates]
    if not rated:
        reason = f"projet {project_id!r} : aucune de ses {len(lines)} lignes n'est notée"
        return insufficient(reason, "ia_no_rated_line")
    reason = f"moyenne des taux d'IA de {len(rated)} lignes de {HISTORY_FILE}"
    return estimated(sum(rated) / len(rated), (HISTORY_SOURCE,), reason, "ia_rate")


def _bases(catalogue):
    """Indexe le catalogue des projets 42 (A4) : `slug` vers `difficulty`, le premier gardé.

    Args:
        catalogue: liste ou tuple de dicts `{slug, name, difficulty}`, ou toute autre valeur.

    Returns:
        Le dict des bases, ou `None` si le catalogue n'est pas une liste.
    """
    if not isinstance(catalogue, (list, tuple)):
        return None
    bases = {}
    for item in catalogue:
        bases.setdefault(item["slug"], item.get("difficulty"))
    return bases


def _base_xp(slug, bases):
    """XP de base d'un projet 42 (`difficulty`), sans facteur d'IA (`c:147`).

    Args:
        slug: identifiant du projet 42, texte.
        bases: dict `slug` vers `difficulty` de `_bases`, ou `None` sans catalogue.

    Returns:
        La valeur `estimated` de la base (source tierce) ; `unmeasurable` de code
        `equivalent_unknown` (catalogue absent ou sans `slug`) ou `base_xp_invalid`.
    """
    if bases is None:
        reason = f"catalogue des projets 42 indisponible : aucune XP de base pour {slug!r}"
        return unmeasurable(reason, UNKNOWN_CODE)
    if slug not in bases:
        return unmeasurable(f"équivalent 42 {slug!r} absent du catalogue", UNKNOWN_CODE)
    base = bases[slug]
    if not is_nonnegative(base):
        reason = f"XP de base {base!r} de {slug!r} : nombre fini non négatif attendu"
        return unmeasurable(reason, "base_xp_invalid")
    reason = "XP de base lue dans le catalogue tiers des projets 42"
    return estimated(base, (CATALOGUE_SOURCE,), reason, THIRD_PARTY_CODE)


def _date_problem(text, today):
    """Renvoie la cause pour laquelle la date d'un projet est suspecte, ou `None`.

    Args:
        text: date ISO de `read_projects`, ou `None`.
        today: `datetime.date` de la synchronisation.

    Returns:
        La raison française, ou `None` pour une date de 2020 au jour de synchronisation.
    """
    if text is None:
        return "date de projet absente : XP non comptée"
    try:
        day = date.fromisoformat(text)
    except (TypeError, ValueError):
        return f"date de projet {text!r} illisible : XP non comptée"
    if day < EARLIEST_DATE:
        return f"date de projet {day} antérieure au {EARLIEST_DATE} : XP non comptée"
    if day > today:
        return f"date de projet {day} postérieure au jour de synchronisation {today}"
    return None


def _project_xp(record, factor, context):
    """Calcule l'XP d'un projet : base de son équivalent 42 multipliée par le facteur.

    Args:
        record: enregistrement utilisable de `projets.csv`.
        factor: valeur statuée du facteur d'IA du projet.
        context: données communes du calcul.

    Returns:
        La valeur `estimated` non arrondie ; sinon, dans l'ordre des refus, `insufficient`
        (`duplicates_42_project`), la base non estimée, le facteur sans valeur, ou
        `insufficient` (`suspect_date`) avec la valeur calculée.
    """
    equivalent = record["equivalent_42"]
    if record["frame"] == PERSONAL and equivalent in context.validated:
        reason = f"projet perso qui reprend le projet 42 validé {equivalent!r} : non compté"
        return insufficient(reason, "duplicates_42_project")
    base = _base_xp(equivalent, context.bases)
    if base.status != ESTIMATED:
        return base
    if factor.status != ESTIMATED:
        return _without_value(factor)
    value = base.value * factor.value
    problem = _date_problem(record["date"], context.today)
    if problem is not None:
        return insufficient(problem, "suspect_date", value)
    reason = "XP de base de l'équivalent 42 (catalogue tiers) multipliée par le facteur d'IA"
    sources = (PROJECTS_SOURCE, HISTORY_SOURCE, CATALOGUE_SOURCE)
    return estimated(value, sources, reason, THIRD_PARTY_CODE)


def _validated_slugs(validated):
    """Renvoie les `slug` des projets 42 validés, vide si la liste est inutilisable."""
    if not isinstance(validated, (list, tuple)):
        return frozenset()
    return frozenset(item["slug"] for item in validated)


def _entry(record, context):
    """Assemble l'entrée `projects[]` d'un enregistrement utilisable (clés de `_PROJECT`)."""
    factor = _ia_factor(record["id"], context.groups, context.rates)
    return {
        "id": record["id"],
        "setting": record["frame"],
        "name": record["id"],
        "status": record["status"],
        "date": record["date"],
        "equivalent_42": record["equivalent_42"],
        "ia_factor": factor,
        "xp": _project_xp(record, factor, context),
    }


@never_raises(empty)
def project_entries(projects, history, catalogue, validated, rules, today):
    """Calcule le facteur d'IA et l'XP de chaque projet perso ou pro.

    Args:
        projects: `read_projects(...).records`, ou `None` si `projets.csv` est absent.
        history: `read_history(...).records`, ou `None`.
        catalogue: liste de `{slug, name, difficulty}` des projets 42 (A4), ou `None`.
        validated: `Api42Result.projects` (`{id, slug, name, final_mark}`), ou `None`.
        rules: dict de `config.load_rules`, dont `ia` est lu.
        today: `datetime.date` de la synchronisation.

    Returns:
        Un tuple de dicts `id`, `setting`, `name`, `status`, `date`, `equivalent_42`,
        `ia_factor`, `xp`, dans l'ordre reçu, sans enregistrement mal formé ni doublon ;
        `()` si une entrée est inutilisable.
    """
    context = _Context(
        _spellings(history),
        _rates(rules),
        _bases(catalogue),
        _validated_slugs(validated),
        today,
    )
    return tuple(_entry(record, context) for record in _kept(projects))


def _author_anomalies(history, rates):
    """Signale les lignes d'historique d'auteur ni noté dans `rules["ia"]` ni `lecture`."""
    if not isinstance(history, (list, tuple)):
        return []
    known = {*rates, READING_AUTHOR}
    return [
        Anomaly(
            HISTORY_FILE,
            line["line"],
            "unknown_author",
            f"auteur {line['author']!r} absent de rules[ia] : ligne ignorée",
        )
        for line in history
        if line["author"] not in known
    ]


def _ambiguity_anomaly(project_id, groups):
    """Renvoie l'anomalie d'une clé ambiguë, à la première ligne de la deuxième graphie."""
    spellings = groups.get(project_id.casefold(), {})
    if len(spellings) <= 1:
        return None
    second = list(spellings.values())[1]
    detail = _ambiguity(project_id, spellings)
    return Anomaly(HISTORY_FILE, second[0]["line"], AMBIGUOUS_CODE, detail)


@never_raises(empty)
def project_anomalies(projects, history, catalogue, validated, rules, today):
    """Signale les projets mal formés ou en doublon et les lignes d'historique fautives.

    Args:
        projects: `read_projects(...).records`, ou `None`.
        history: `read_history(...).records`, ou `None`.
        catalogue: reçu comme pour `project_entries`, non lu.
        validated: reçu comme pour `project_entries`, non lu.
        rules: dict de `config.load_rules`, dont `ia` est lu.
        today: reçu comme pour `project_entries`, non lu (une date suspecte est déjà
            signalée par `read_projects`).

    Returns:
        Un tuple d'`Anomaly` : `malformed_project` et `duplicate_project` (`projets.csv`),
        puis `unknown_author` et `ambiguous_project_key` (`historique-ia.csv`, une par `id`).
    """
    scanned = _scan(projects)
    found = [
        Anomaly(PROJECTS_FILE, record.get("line"), kind, detail)
        for record, kind, detail in scanned
        if kind is not None
    ]
    found += _author_anomalies(history, _rates(rules))
    groups = _spellings(history) or {}
    ambiguities = (
        _ambiguity_anomaly(record["id"], groups)
        for record, kind, _ in scanned
        if kind is None
    )
    found += [anomaly for anomaly in ambiguities if anomaly is not None]
    return tuple(found)


def _table_value(state, noun):
    """Rend une XP de `xp_table.xp_for_level` telle quelle, `unmeasurable` si non statuée."""
    if isinstance(state, StatedValue):
        return state
    reason = f"{noun} : valeur reçue {state!r}, table XP indisponible"
    return unmeasurable(reason, "xp_table_unavailable")


def _validated_projects(validated, bases):
    """Renvoie un `{id, name, base_xp}` par projet 42 validé, ou `None` sans liste."""
    if not isinstance(validated, (list, tuple)):
        return None
    return tuple(
        {
            "id": item["slug"],
            "name": item["name"],
            "base_xp": _base_xp(item["slug"], bases),
        }
        for item in validated
    )


def _unexplained_gap(xp_state, projects):
    """Calcule l'écart non expliqué : XP du niveau moins la somme des XP de base (`c:62`).

    Args:
        xp_state: valeur statuée de l'XP du niveau 42.
        projects: tuple de `_validated_projects`, ou `None` sans liste de projets validés.

    Returns:
        La valeur `estimated`, ou l'`unmeasurable` du premier terme qui manque.
    """
    if projects is None:
        reason = "projets 42 validés indisponibles : écart non expliqué inconnu"
        return unmeasurable(reason, API_CODE)
    for term in (xp_state, *(item["base_xp"] for item in projects)):
        missing = missing_measure(term, "terme de l'écart", XP_INVALID_CODE)
        if missing is not None:
            return missing
    value = xp_state.value - sum(item["base_xp"].value for item in projects)
    return estimated(value, (API_SOURCE, CATALOGUE_SOURCE))


def _empty_level42(error):
    """Entité `level42` de repli : valeurs `unmeasurable`, aucun projet."""
    missing = unmeasurable(f"données du niveau 42 inutilisables : {error}", API_CODE)
    return {
        "level": missing,
        "xp": missing,
        "target_xp": missing,
        "projects": (),
        "unexplained_gap": missing,
    }


@never_raises(_empty_level42)
def level42_entity(level, xp, target_xp, validated, catalogue):
    """Construit l'entité `level42` : niveau, XP, cible, projets validés et écart.

    Args:
        level: `Api42Result.level` (valeur statuée), ou `None`.
        xp: `xp_table.xp_for_level` du niveau, ou `None`.
        target_xp: `xp_table.xp_for_level` de `calibration.target_level`, ou `None`.
        validated: `Api42Result.projects`, ou `None`.
        catalogue: liste de `{slug, name, difficulty}` des projets 42, ou `None`.

    Returns:
        Le dict `level`, `xp`, `target_xp`, `projects` (tuple), `unexplained_gap` ;
        un niveau non mesuré rend `xp` et l'écart `unmeasurable` de son code.
    """
    missing = missing_measure(level, "niveau 42", "level_invalid")
    xp_state = _table_value(xp, "XP du niveau 42") if missing is None else missing
    projects = _validated_projects(validated, _bases(catalogue))
    return {
        "level": level if missing is None else missing,
        "xp": xp_state,
        "target_xp": _table_value(target_xp, "XP cible"),
        "projects": () if projects is None else projects,
        "unexplained_gap": _unexplained_gap(xp_state, projects),
    }


def is_counted(entry):
    """Dit si un projet compte dans l'XP Système : livré et d'XP estimée (`c:67`)."""
    xp_state = entry["xp"]
    return (
        entry["status"] == DELIVERED
        and isinstance(xp_state, StatedValue)
        and xp_state.status == ESTIMATED
    )


def _setting_total(counted, setting):
    """Somme non arrondie, en flottant, de l'XP des projets comptés d'un cadre."""
    return float(
        sum(
            entry["xp"].value
            for entry in counted
            if entry["setting"] == setting
        )
    )


def _project_origins(entries):
    """Renvoie l'XP `perso` puis `pro` des projets comptés, sommes non arrondies.

    Args:
        entries: tuple de `project_entries`, ou `None` si `projets.csv` est absent.

    Returns:
        Un tuple de valeurs `estimated` ; `unmeasurable` (`no_personal_project`) sans
        `projets.csv`.
    """
    if entries is None:
        return (unmeasurable(NO_PROJECT, NO_PROJECT_CODE),) * len(PROJECT_SETTINGS)
    counted = [entry for entry in entries if is_counted(entry)]
    return tuple(
        estimated(_setting_total(counted, setting), (PROJECTS_SOURCE,))
        for setting in PROJECT_SETTINGS
    )


def _system(total, origins):
    """Assemble `{xp, origins}` ; `origins` suit l'ordre de `ORIGINS`."""
    return {
        "xp": total,
        "origins": tuple(
            {"origin": name, "xp": state}
            for name, state in zip(ORIGINS, origins)
        ),
    }


def _empty_system(error):
    """Valeur `system` de repli : XP et trois origines `unmeasurable`."""
    missing = unmeasurable(f"XP Système non calculable : {error}", XP_INVALID_CODE)
    return _system(missing, (missing,) * len(ORIGINS))


@never_raises(_empty_system)
def system_xp(xp_42, entries):
    """Calcule l'XP Système : XP 42 plus l'XP des projets perso et pro comptés (`c:66`).

    Args:
        xp_42: valeur `xp` de `level42_entity`, ou `None`.
        entries: tuple de `project_entries`, ou `None` si `projets.csv` est absent.

    Returns:
        Le dict `xp` (entier arrondi à la moitié vers le haut, A6) et `origins` (`42`,
        `perso`, `pro`) ; sans `projets.csv`, `xp` porte le code `no_personal_project` ;
        une XP 42 non mesurée rend `xp` et l'origine `42` `unmeasurable` de son code.
    """
    origins = _project_origins(entries)
    missing = missing_measure(xp_42, "XP 42", XP_INVALID_CODE)
    if missing is not None:
        return _system(missing, (missing, *origins))
    added = sum(state.value for state in origins if state.status == ESTIMATED)
    total = math.floor(xp_42.value + added + HALF)
    if entries is None:
        xp_state = estimated(total, xp_42.sources, NO_PROJECT, NO_PROJECT_CODE)
    else:
        xp_state = estimated(total, (*xp_42.sources, PROJECTS_SOURCE))
    return _system(xp_state, (xp_42, *origins))
