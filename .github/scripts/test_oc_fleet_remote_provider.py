"""Offline contract for the opt-in private Ollama provider. No model/network use."""
import json
import unittest
from pathlib import Path

from oc_fleet_contract import MODELS, REMOTE_MODEL, REMOTE_OLLAMA_URL, provider_configuration


class ReviewedLocalProviderTests(unittest.TestCase):
    def test_approved_remote_model_has_fixed_tailnet_url(self):
        cfg=provider_configuration(REMOTE_MODEL)
        self.assertEqual(REMOTE_MODEL,"ollama-remote/qwen3:4b-instruct")
        self.assertEqual(cfg["ollama-remote"]["options"]["baseURL"],
                         REMOTE_OLLAMA_URL+"/v1")
        self.assertEqual(sorted(cfg["ollama-remote"]["models"]), ["qwen3:4b-instruct"])
        self.assertNotIn("apiKey",cfg["ollama-remote"]["options"])
        self.assertNotIn("http://",json.dumps(cfg))

    def test_legacy_free_models_are_unmodified(self):
        for model in MODELS-{REMOTE_MODEL}:
            with self.subTest(model=model):
                self.assertEqual(provider_configuration(model),{})

    def test_unknown_model_and_url_are_refused(self):
        for model in (None,"ollama/qwen3:4b-instruct","ollama-remote/any",
                      "http://localhost:11434/v1","ollama-remote/qwen3:4b-instruct ",
                      "opencode/paid-model",{}):
            with self.subTest(model=repr(model)),self.assertRaises(ValueError):
                provider_configuration(model)

    def test_private_identity_missing_stops_before_tailnet_join(self):
        y=(Path(__file__).parent.parent/"workflows"/"oc-fleet-worker.yml").read_text()
        preflight=y.index("name: Verify Tailscale federated identity is configured")
        join=y.index("name: Join private Tailnet for reviewed local Ollama")
        agent=y.index("name: Execute unprivileged temporary agent")
        self.assertLess(preflight,join)
        self.assertLess(join,agent)
        text=y[preflight:join]
        self.assertIn("if: needs.validate.outputs.model == 'ollama-remote/qwen3:4b-instruct'",text)
        self.assertIn("secrets.TS_OAUTH_CLIENT_ID",text)
        self.assertIn("secrets.TS_AUDIENCE",text)
        self.assertIn('if [ -z "$FLEET_TS_CLIENT_ID" ] || [ -z "$FLEET_TS_AUDIENCE" ]; then',text)
        self.assertIn('exit 1',text)
        self.assertNotIn('set -x',text)
        self.assertNotIn('echo "$FLEET_TS_CLIENT_ID"',text)
        self.assertNotIn('echo "$FLEET_TS_AUDIENCE"',text)

    def test_manual_tailnet_smoke_is_read_only_and_never_starts_models(self):
        y=(Path(__file__).parent.parent/"workflows"/"oc-fleet-tailnet-smoke.yml").read_text()
        self.assertIn("workflow_dispatch:",y)
        self.assertIn("github.ref == 'refs/heads/main'",y)
        self.assertIn("id-token: write",y)
        self.assertIn("tailscale/github-action@99a8333667fff04fdd6cffb46dfd409f8329a7bf",y)
        self.assertIn("secrets.TS_OAUTH_CLIENT_ID",y)
        self.assertIn("secrets.TS_AUDIENCE",y)
        self.assertIn("tag:ci",y)
        self.assertIn("/api/version",y)
        self.assertIn("/api/tags",y)
        self.assertNotIn("/api/chat",y)
        self.assertNotIn("/api/generate",y)
        self.assertNotIn("opencode run",y)
        self.assertNotIn("gh workflow run",y)
        self.assertNotIn("funnel",y.lower())
        self.assertNotIn("on: push",y)
        self.assertNotIn("pull_request:",y)

    def test_action_is_opt_in_and_uses_oidc_not_shared_authkey(self):
        y=(Path(__file__).parent.parent/"workflows"/"oc-fleet-worker.yml").read_text()
        self.assertIn("if: needs.validate.outputs.model == 'ollama-remote/qwen3:4b-instruct'",y)
        self.assertIn("tailscale/github-action@99a8333667fff04fdd6cffb46dfd409f8329a7bf",y)
        self.assertIn("audience: ${{ secrets.TS_AUDIENCE }}",y)
        self.assertIn("oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}",y)
        self.assertNotIn("funnel",y.lower())
        self.assertNotIn("authkey:",y)
        self.assertIn("provider_configuration(os.environ",y)


if __name__=="__main__":
    unittest.main()
