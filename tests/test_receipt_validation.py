from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
ARO_ROOT = WORKSPACE_ROOT / "aro-audit"

if str(ARO_ROOT) not in sys.path:
    sys.path.insert(0, str(ARO_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aro_audit.receipt_validation import validate_receipt
from examples.enterprise_sandbox_demo.run import _summarize_receipt_validation


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ReceiptValidationIntegrationTests(unittest.TestCase):
    def test_valid_receipt_fixture_passes(self) -> None:
        result = validate_receipt(FIXTURES / "enterprise_sandbox_receipt.valid.json")
        self.assertTrue(result.valid)
        self.assertEqual(result.profile, "minimal")

    def test_invalid_receipt_fixture_fails_with_reason(self) -> None:
        result = validate_receipt(FIXTURES / "enterprise_sandbox_receipt.invalid.json")
        self.assertFalse(result.valid)
        self.assertIn("hashes.event_hash", result.reason)

    def test_summary_contract_never_returns_null(self) -> None:
        receipt = json.loads(
            (FIXTURES / "enterprise_sandbox_receipt.invalid.json").read_text(encoding="utf-8")
        )
        summary = _summarize_receipt_validation(receipt)
        self.assertIs(summary["receipt_valid"], False)
        self.assertEqual(summary["receipt_validation_profile"], "minimal")
        self.assertIsInstance(summary["receipt_validation_reason"], str)
        self.assertTrue(summary["receipt_validation_reason"])


if __name__ == "__main__":
    unittest.main()
