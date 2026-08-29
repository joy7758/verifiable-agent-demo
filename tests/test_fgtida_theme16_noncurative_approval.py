from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from paper_eval import runner
from paper_eval.common import ROOT_DIR, load_json
from paper_eval.suite import find_task


class NonCurativeHumanApprovalTests(unittest.TestCase):
    def test_satisfied_human_approval_does_not_override_action_tamper_detection(
        self,
    ) -> None:
        task = deepcopy(find_task("task-015"))
        task["approval_policy"] = {
            **task["approval_policy"],
            "requires_approval": True,
            "approval_scope": "tamper_sensitive_run",
            "approval_token": "test-human-approval-present",
        }

        self.assertEqual(task["tamper_case"]["tamper_target"], "action")
        self.assertEqual(task["tamper_case"]["tamper_method"], "digest_mismatch")

        # Exercise the existing evidence-chain runner end to end. The patched run
        # directory keeps generated evidence isolated and removes it after the test.
        with TemporaryDirectory(prefix=".theme16-test-", dir=ROOT_DIR) as temp_root:
            with patch.object(runner, "RUNS_DIR", Path(temp_root)):
                run_dir = runner.run_task(task, "evidence_chain")

            action = load_json(run_dir / "action.json")
            result = load_json(run_dir / "result.json")
            trace = load_json(run_dir / "trace.json")
            receipt = load_json(run_dir / "receipt.json")

        policy_decision = action["policy"]["decision"]
        self.assertTrue(action["policy"]["approval_policy"]["requires_approval"])
        self.assertEqual(
            action["policy"]["approval_policy"]["approval_token"],
            "test-human-approval-present",
        )
        self.assertTrue(policy_decision["approval_satisfied"])
        self.assertEqual(policy_decision["status"], "approved")
        self.assertEqual(action["authorization_state"], "approved")

        integrity = trace["integrity"]
        self.assertNotEqual(
            integrity["subject_digests"]["action.json"],
            integrity["expected_digests"]["action.json"],
        )
        self.assertEqual(integrity["verification_status"], "tamper_detected")
        self.assertEqual(result["status"], "tamper_detected")
        self.assertNotEqual(result["status"], "completed")
        self.assertTrue(
            receipt["audit_receipt"]["integrity_summary"]["tamper_detected"]
        )


if __name__ == "__main__":
    unittest.main()
