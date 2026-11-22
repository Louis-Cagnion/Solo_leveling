"""Tests de `system_sync.model` (T2, cas N1 à N4, L4 à L7 et L14, amendements A17 et A18).

Contrat de T2.b, import `from system_sync import model` :
- `STATUSES = ("observed", "estimated", "insufficient", "unmeasurable")` (A17).
- `REASON_CODES` : ensemble fermé de codes en anglais (A18). Il contient au moins ceux
  des fixtures : `api_unavailable`, `xp_interpolated`, `third_party_table`, `ia_rate`,
  `below_threshold`, `certification_list_unreadable`, `no_certification_notion`,
  `full_list_unavailable`, `no_personal_project`, `card_unmeasurable`.
- `ModelError(ValueError)` : message qui nomme le champ (`value`, `status`, `sources`,
  `reason`, `reason_code`) et la valeur reçue.
- `StatedValue(value, status, sources=(), reason=None, reason_code=None)` : dataclass
  figée, invariants vérifiés à la création. `observed` : valeur non nulle, une source au
  moins. `insufficient` : raison non vide, valeur facultative. `unmeasurable` : valeur
  `None`, raison non vide. `estimated` : libre. `reason_code` appartient à
  `REASON_CODES` et accompagne toute raison non vide, obligatoire pour `insufficient` et
  `unmeasurable`. `.to_dict()` donne `{"value", "status", "sources": list, "reason",
  "reason_code"}`.
- `observed(value, sources)`, `estimated(value, sources, reason=None, reason_code=None)`,
  `insufficient(reason, reason_code, value=None)`, `unmeasurable(reason, reason_code)`
  renvoient une `StatedValue`.
- `Anomaly(file, line, kind, detail)` : dataclass figée ; `str()` donne
  `fichier:ligne : nature : détail` ; `.to_dict()` donne les quatre champs.
"""

import unittest

try:
    from system_sync import model
except ImportError:
    model = None  # chaque test échoue séparément tant que le module manque

CODE = "api_unavailable"
FIXTURE_CODES = {
    "api_unavailable",
    "xp_interpolated",
    "third_party_table",
    "ia_rate",
    "below_threshold",
    "certification_list_unreadable",
    "no_certification_notion",
    "full_list_unavailable",
    "no_personal_project",
    "card_unmeasurable",
}


class StatedValueTest(unittest.TestCase):
    def test_T2_N1_statuses_are_the_four_english_names(self):
        self.assertEqual(
            model.STATUSES,
            ("observed", "estimated", "insufficient", "unmeasurable"),
        )

    def test_T2_N1_observed_value(self):
        stated = model.observed(12.44, ["api42"])
        self.assertEqual(
            stated.to_dict(),
            {
                "value": 12.44,
                "status": "observed",
                "sources": ["api42"],
                "reason": None,
                "reason_code": None,
            },
        )

    def test_T2_N2_estimated_value_keeps_its_reason_and_code(self):
        stated = model.estimated(
            133834,
            ["xp_table"],
            reason="interpolation linéaire",
            reason_code="xp_interpolated",
        )
        self.assertEqual(
            stated.to_dict(),
            {
                "value": 133834,
                "status": "estimated",
                "sources": ["xp_table"],
                "reason": "interpolation linéaire",
                "reason_code": "xp_interpolated",
            },
        )

    def test_T2_N2_estimated_value_without_reason(self):
        stated = model.estimated(7, ["xp_table"])
        self.assertEqual(stated.to_dict()["status"], "estimated")
        self.assertIsNone(stated.to_dict()["reason"])
        self.assertIsNone(stated.to_dict()["reason_code"])

    def test_T2_N3_insufficient_value_has_a_reason_and_a_code(self):
        stated = model.insufficient("moins de 3 projets", "below_threshold")
        self.assertEqual(
            stated.to_dict(),
            {
                "value": None,
                "status": "insufficient",
                "sources": [],
                "reason": "moins de 3 projets",
                "reason_code": "below_threshold",
            },
        )

    def test_T2_N3_direct_construction_matches_the_helper(self):
        direct = model.StatedValue(None, "insufficient", (), "manque", CODE)
        self.assertEqual(direct, model.insufficient("manque", CODE))

    def test_A17_unmeasurable_value_is_null_with_reason_and_code(self):
        stated = model.unmeasurable(
            "aucun projet perso ou pro enregistré",
            "no_personal_project",
        )
        self.assertEqual(
            stated.to_dict(),
            {
                "value": None,
                "status": "unmeasurable",
                "sources": [],
                "reason": "aucun projet perso ou pro enregistré",
                "reason_code": "no_personal_project",
            },
        )

    def test_A17_unmeasurable_direct_construction_matches_the_helper(self):
        direct = model.StatedValue(None, "unmeasurable", (), "manque", CODE)
        self.assertEqual(direct, model.unmeasurable("manque", CODE))

    def test_A17_insufficient_value_is_optional(self):
        stated = model.insufficient("calibration provisoire", "below_threshold", value=12.6)
        self.assertEqual(stated.to_dict()["value"], 12.6)
        self.assertEqual(stated.to_dict()["status"], "insufficient")

    def test_A18_vocabulary_is_closed_and_in_english(self):
        self.assertIsInstance(model.REASON_CODES, (frozenset, tuple))
        self.assertTrue(FIXTURE_CODES <= set(model.REASON_CODES))
        for code in model.REASON_CODES:
            self.assertRegex(code, r"^[a-z][a-z0-9_]*$", code)


class AnomalyTest(unittest.TestCase):
    def test_T2_N4_anomaly_renders_file_and_line(self):
        anomaly = model.Anomaly("relations.csv", 40, "ligne mal formée", "virgule")
        self.assertEqual(str(anomaly), "relations.csv:40 : ligne mal formée : virgule")

    def test_T2_N4_anomaly_to_dict(self):
        anomaly = model.Anomaly("relations.csv", 40, "ligne mal formée", "virgule")
        self.assertEqual(
            anomaly.to_dict(),
            {
                "file": "relations.csv",
                "line": 40,
                "kind": "ligne mal formée",
                "detail": "virgule",
            },
        )


class InvariantsTest(unittest.TestCase):
    def test_T2_L4_unknown_status_names_the_value(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(1, "bizarre", ["api42"])
        self.assertIn("status", str(ctx.exception))
        self.assertIn("bizarre", str(ctx.exception))

    def test_T2_L4_french_status_names_are_refused(self):
        for status in ("observe", "estime", "insuffisant", "non mesurable", "", None):
            with self.assertRaises(model.ModelError, msg=repr(status)):
                model.StatedValue(1, status, ["api42"])

    def test_T2_L5_observed_with_null_value(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.observed(None, ["api42"])
        self.assertIn("value", str(ctx.exception))

    def test_T2_L6_unmeasurable_with_value(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(5, "unmeasurable", [], "manque", CODE)
        self.assertIn("value", str(ctx.exception))
        self.assertIn("5", str(ctx.exception))

    def test_T2_L7_insufficient_and_unmeasurable_without_usable_reason(self):
        for status in ("insufficient", "unmeasurable"):
            for reason in (None, "", "   ", "\t\n "):
                with self.assertRaises(model.ModelError, msg=f"{status} {reason!r}") as ctx:
                    model.StatedValue(None, status, [], reason, CODE)
                self.assertIn("reason", str(ctx.exception))

    def test_T2_L7_helpers_refuse_blank_reason(self):
        for helper in (model.insufficient, model.unmeasurable):
            for reason in (None, "", "   "):
                with self.assertRaises(model.ModelError, msg=repr(reason)):
                    helper(reason, CODE)

    def test_T2_L14_observed_without_source(self):
        for sources in ([], (), None):
            with self.assertRaises(model.ModelError, msg=repr(sources)) as ctx:
                model.StatedValue(3, "observed", sources)
            self.assertIn("sources", str(ctx.exception))

    def test_A17_unmeasurable_without_reason_code(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(None, "unmeasurable", [], "manque", None)
        self.assertIn("reason_code", str(ctx.exception))

    def test_A18_insufficient_without_reason_code(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(None, "insufficient", [], "manque", None)
        self.assertIn("reason_code", str(ctx.exception))

    def test_A18_estimated_reason_without_code(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(7, "estimated", ["xp_table"], "table tierce", None)
        self.assertIn("reason_code", str(ctx.exception))

    def test_A18_code_outside_the_vocabulary_names_the_value(self):
        cases = (("insufficient", None), ("unmeasurable", None), ("estimated", 7))
        for status, value in cases:
            with self.assertRaises(model.ModelError, msg=status) as ctx:
                model.StatedValue(value, status, ["xp_table"], "manque", "code_invente")
            self.assertIn("reason_code", str(ctx.exception))
            self.assertIn("code_invente", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
