"""Tests de `system_sync.model` (T2, cas N1 à N4, L4 à L7 et L14).

Contrat de T2.b, import `from system_sync import model` :
- `STATUSES = ("observed", "estimated", "insufficient")`.
- `ModelError(ValueError)` : message qui nomme le champ (`value`, `status`,
  `sources`, `reason`) et la valeur reçue.
- `StatedValue(value, status, sources=(), reason=None)` : dataclass figée, invariants
  vérifiés à la création. `observed` : valeur non nulle, une source au moins.
  `insufficient` : valeur `None`, raison non vide. `estimated` : libre.
  `.to_dict()` donne `{"value", "status", "sources": list, "reason"}`.
- `observed(value, sources)`, `estimated(value, sources, reason=None)`,
  `insufficient(reason)` renvoient une `StatedValue`.
- `Anomaly(file, line, kind, detail)` : dataclass figée ; `str()` donne
  `fichier:ligne : nature : détail` ; `.to_dict()` donne les quatre champs.
"""

import unittest

try:
    from system_sync import model
except ImportError:
    model = None  # chaque test échoue séparément tant que le module manque


class StatedValueTest(unittest.TestCase):
    def test_T2_N1_statuses_are_the_three_english_names(self):
        self.assertEqual(model.STATUSES, ("observed", "estimated", "insufficient"))

    def test_T2_N1_observed_value(self):
        stated = model.observed(12.44, ["api42"])
        self.assertEqual(
            stated.to_dict(),
            {"value": 12.44, "status": "observed", "sources": ["api42"], "reason": None},
        )

    def test_T2_N2_estimated_value_keeps_its_reason(self):
        stated = model.estimated(133834, ["xp_table"], reason="interpolation linéaire")
        self.assertEqual(
            stated.to_dict(),
            {
                "value": 133834,
                "status": "estimated",
                "sources": ["xp_table"],
                "reason": "interpolation linéaire",
            },
        )

    def test_T2_N2_estimated_value_without_reason(self):
        stated = model.estimated(7, ["xp_table"])
        self.assertEqual(stated.to_dict()["status"], "estimated")
        self.assertIsNone(stated.to_dict()["reason"])

    def test_T2_N3_insufficient_value_is_null_with_reason(self):
        stated = model.insufficient("aucun projet perso ou pro enregistré")
        self.assertEqual(
            stated.to_dict(),
            {
                "value": None,
                "status": "insufficient",
                "sources": [],
                "reason": "aucun projet perso ou pro enregistré",
            },
        )

    def test_T2_N3_direct_construction_matches_the_helper(self):
        direct = model.StatedValue(None, "insufficient", reason="manque")
        self.assertEqual(direct, model.insufficient("manque"))


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
        for status in ("observe", "estime", "insuffisant", "", None):
            with self.assertRaises(model.ModelError, msg=repr(status)):
                model.StatedValue(1, status, ["api42"])

    def test_T2_L5_observed_with_null_value(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.observed(None, ["api42"])
        self.assertIn("value", str(ctx.exception))

    def test_T2_L6_insufficient_with_value(self):
        with self.assertRaises(model.ModelError) as ctx:
            model.StatedValue(5, "insufficient", [], "manque")
        self.assertIn("value", str(ctx.exception))
        self.assertIn("5", str(ctx.exception))

    def test_T2_L7_insufficient_without_usable_reason(self):
        for reason in (None, "", "   ", "\t\n "):
            with self.assertRaises(model.ModelError, msg=repr(reason)) as ctx:
                model.StatedValue(None, "insufficient", [], reason)
            self.assertIn("reason", str(ctx.exception))

    def test_T2_L7_helper_refuses_blank_reason(self):
        for reason in (None, "", "   "):
            with self.assertRaises(model.ModelError, msg=repr(reason)):
                model.insufficient(reason)

    def test_T2_L14_observed_without_source(self):
        for sources in ([], (), None):
            with self.assertRaises(model.ModelError, msg=repr(sources)) as ctx:
                model.StatedValue(3, "observed", sources)
            self.assertIn("sources", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
