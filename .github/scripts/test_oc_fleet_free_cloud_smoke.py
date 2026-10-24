"""Offline contract for one bounded OpenCode free-model Actions diagnostic."""
from pathlib import Path
import unittest

PATH=Path(__file__).parent.parent/"workflows"/"oc-fleet-free-model-smoke.yml"

class CloudSmokeContractTests(unittest.TestCase):
    def test_is_manual_read_only_cloud_only(self):
        s=PATH.read_text()
        self.assertIn("workflow_dispatch:",s)
        self.assertIn("permissions: {}",s)
        self.assertIn("github.repository == 'MakerParsDev/oc-test'",s)
        self.assertIn("github.ref == 'refs/heads/main'",s)
        self.assertNotIn("actions/checkout",s)
        self.assertNotIn("tailscale",s.lower())
        self.assertNotIn("ollama",s.lower())
        self.assertNotIn("DOPPLER_TOKEN",s)
        self.assertNotIn("gh workflow run",s)
        self.assertNotIn("on: push",s)
        self.assertNotIn("pull_request:",s)

    def test_has_single_request_no_hidden_fallback(self):
        s=PATH.read_text()
        self.assertIn("@opencode/cli@2.1.4",s)
        self.assertEqual(s.count("opencode run --standalone"),1)
        self.assertIn("timeout --signal=TERM",s)
        self.assertIn("90s opencode run",s)
        self.assertIn('category=PROVIDER_ACCESS',s)
        self.assertIn('category=RATE_LIMIT',s)
        self.assertIn('category=SUCCESS',s)
        self.assertIn('test "$category" = SUCCESS',s)
        self.assertIn('OPENCODE_CONFIG_CONTENT=',s)
        self.assertNotIn('"*":"deny"',s)

    def test_never_exposes_raw_model_output(self):
        s=PATH.read_text()
        self.assertIn('>"$scratch/model.log" 2>&1',s)
        self.assertNotIn('cat "$scratch/model.log"',s)
        self.assertNotIn('upload-artifact',s)
        self.assertNotIn('set -x',s)


if __name__=="__main__":
    unittest.main()
