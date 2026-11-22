"""Tests de `output` : validateur sans exception et contenu des feuilles (I2, I3)."""

import tempfile
import unittest
from pathlib import Path

from tests.system_sync.test_output import StateCase, load_state, paths_of, set_at, vpath

try:
    from system_sync import output
except ImportError:
    output = None  # chaque test échoue séparément tant que le module manque


class ValidatorNeverRaisesTest(StateCase):
    def refused_and_not_written(self, dotted, value):
        state = load_state("complete")
        set_at(state, dotted, value)
        self.assertIn(vpath(dotted), paths_of(state), repr(value))
        target = Path(tempfile.mkdtemp()) / "state.js"
        self.addCleanup(target.parent.rmdir)
        self.addCleanup(target.unlink, missing_ok=True)
        output.write(load_state("minimal"), target)
        before = target.read_bytes()
        with self.assertRaises(output.OutputError):
            output.write(state, target)
        self.assertEqual(target.read_bytes(), before)

    def test_I2_unhashable_id_is_a_problem_not_a_type_error(self):
        self.refused_and_not_written("cards.0.id", ["a"])

    def test_I2_unhashable_source_name_is_a_problem(self):
        self.refused_and_not_written("sources.0.name", {"a": 1})

    def test_I2_huge_integer_is_a_problem_not_an_overflow(self):
        self.refused_and_not_written("level42.xp.value", 10**400)


class LeafContentTest(StateCase):
    def test_I3_json_leaf_refuses_nan_at_the_nested_path(self):
        state = load_state("complete")
        set_at(state, "system.calibration.value", {"r": float("nan")})
        paths = paths_of(state)
        self.assertTrue(
            any(p.startswith("system.calibration.value.r") for p in paths),
            paths,
        )

    def test_I3_json_leaf_refuses_set_and_bytes(self):
        for value in ({1, 2}, b"x"):
            state = load_state("complete")
            set_at(state, "system.calibration.value", value)
            paths = paths_of(state)
            self.assertTrue(
                any(p.startswith("system.calibration.value") for p in paths),
                (value, paths),
            )

    def test_I3_text_refuses_a_lone_surrogate(self):
        state = load_state("complete")
        set_at(state, "notions.notion_a.label", "a\ud800b")
        paths = paths_of(state)
        self.assertTrue(
            any(p.startswith("notions.notion_a.label") for p in paths),
            paths,
        )

    def test_I3_finite_json_object_with_text_keys_stays_valid(self):
        self.accepted("system.calibration.value", {"r": 1.5, "pts": [1, 2]})


if __name__ == "__main__":
    unittest.main()
