"""Offline contract for four isolated cloud-model editing agents."""
from pathlib import Path
import unittest

WORKFLOW=(Path(__file__).parent.parent/"workflows"/"oc-fleet-parallel-agent-smoke.yml").read_text()

class ParallelAcceptanceTests(unittest.TestCase):
    def test_four_isolated_hosted_runners_without_repo_access(self):
        self.assertIn("workflow_dispatch:",WORKFLOW)
        self.assertIn("permissions: {}",WORKFLOW)
        self.assertIn("github.repository == 'MakerParsDev/oc-test'",WORKFLOW)
        self.assertIn("github.ref == 'refs/heads/main'",WORKFLOW)
        self.assertIn("max-parallel: 4",WORKFLOW)
        self.assertIn("slot: [1, 2, 3, 4]",WORKFLOW)
        self.assertIn("fail-fast: false",WORKFLOW)
        self.assertNotIn("actions/checkout",WORKFLOW)
        self.assertNotIn("tailscale",WORKFLOW.lower())
        self.assertNotIn("ollama",WORKFLOW.lower())
        self.assertNotIn("DOPPLER_TOKEN",WORKFLOW)
        self.assertNotIn("on: push",WORKFLOW)
        self.assertNotIn("pull_request:",WORKFLOW)

    def test_one_agent_edit_per_slot_with_bounded_tools(self):
        self.assertIn("@opencode/cli@2.1.4",WORKFLOW)
        self.assertEqual(WORKFLOW.count("opencode run --standalone"),1)
        self.assertIn("timeout --signal=TERM --kill-after=5s 120s",WORKFLOW)
        self.assertIn('"bash":"deny"',WORKFLOW)
        self.assertIn('"edit":"allow"',WORKFLOW)
        self.assertIn("No actual file edit",WORKFLOW)
        self.assertIn('files==["calculator.py"]',WORKFLOW)
        self.assertIn("FLEET_AGENT_EDIT_VERIFIED",WORKFLOW)

    def test_no_leaks_or_commit(self):
        self.assertIn('>"$scratch/opencode.log" 2>&1',WORKFLOW)
        self.assertNotIn('cat "$scratch/opencode.log"',WORKFLOW)
        self.assertNotIn("upload-artifact",WORKFLOW)
        self.assertNotIn("gh pr create",WORKFLOW)
        self.assertNotIn("git push",WORKFLOW)
        self.assertNotIn("set -x",WORKFLOW)

if __name__=="__main__":
    unittest.main()
