"""Offline regression tests for bounded model-failure receipts."""
import json
import tempfile
import unittest
from pathlib import Path

from oc_fleet_contract import FAILURE_CATEGORIES, safe_failure_category, create_failure_evidence


class FailureCategoryTest(unittest.TestCase):
    def test_allowed_codes_have_failure_only_evidence(self):
        m={"task_id":"gh-276-test","source":"rules","repository":"oaslananka/fovux-kit",
           "checkout_sha":"a"*40,"issue_key":"GH-276"}
        with tempfile.TemporaryDirectory() as tmp:
            for code in FAILURE_CATEGORIES:
                with self.subTest(code=code):
                    result=create_failure_evidence(m,tmp,40038275267,1,code)
                    self.assertEqual(result["failure_category"],code)
                    self.assertEqual(result["paths"],[])
                    self.assertFalse(result["published"])
                    self.assertEqual(result["outcome"],"FAILED")
                    self.assertIsNone(result["patch_sha256"])
                    self.assertEqual(json.loads((Path(tmp)/"result.json").read_text()),result)

    def test_raw_provider_text_cannot_leak(self):
        for code in (None,"",42,[],{},"403 TOKEN=secret","PROVIDER_ACCESS\\nSECRET","NONE"):
            with self.subTest(code=repr(code)):
                self.assertEqual(safe_failure_category(code),"AGENT_ERROR")


if __name__=="__main__":
    unittest.main()
