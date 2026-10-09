"""Counter-controls / 反例对照；不声称验证真人能力。"""
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "theme16_fixture", Path(__file__).resolve().parents[1] / "examples/theme16_intervention/run.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InterventionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "intent": {"action_digest": "D1", "commitment_tick": 10},
            "decision": {"action_digest": "D1", "tick": 9},
            "acknowledgement": {"received": True},
            "observation": {"digest": "D1", "deadline": 10, "status": "CANCELLED",
                            "value": 0, "committed": None, "applied": 9},
        }

    def test_acknowledgement_change_does_not_change_effect(self):
        other = deepcopy(self.evidence)
        other["acknowledgement"]["received"] = False
        self.assertEqual(MODULE.assess(other), MODULE.assess(self.evidence))

    def test_positive_ack_does_not_overwrite_actual_execution(self):
        self.evidence["observation"].update(status="EXECUTED", value=1, committed=10, applied=None)
        self.assertEqual(MODULE.assess(self.evidence), {"effect": "EXECUTED", "intervention": "INEFFECTIVE"})

    def test_missing_readback_stays_unknown(self):
        self.evidence["observation"] = None
        self.assertEqual(MODULE.assess(self.evidence), {"effect": "UNKNOWN", "intervention": "NOT_ESTABLISHED"})

    def test_unrelated_readback_cannot_establish_success(self):
        self.evidence["observation"]["digest"] = "OTHER_ACTION"
        self.assertEqual(MODULE.assess(self.evidence)["effect"], "UNKNOWN")

    def test_inconsistent_boundary_observation_cannot_establish_success(self):
        self.evidence["observation"]["applied"] = 10
        self.assertEqual(MODULE.assess(self.evidence)["intervention"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
