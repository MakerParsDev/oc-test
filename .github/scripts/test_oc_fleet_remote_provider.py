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
