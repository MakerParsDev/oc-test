"""Offline regression tests for agent-selection config, without a model call."""
import json
import os
import unittest
from unittest.mock import patch

from oc_fleet_contract import AGENTS, agent_configuration
from oc_fleet_agent_runtime import main, validate_agent_config


class AgentConfigRuntimeTests(unittest.TestCase):
    def test_each_reviewed_role_passes_with_exact_generated_config(self):
        for selected in AGENTS:
            with self.subTest(selected=selected):
                config={"model":"opencode/big-pickle","default_agent":selected}
                role=agent_configuration(selected)
                if role:
                    config["agent"]=role
                self.assertIsNone(validate_agent_config(config,selected))

    def test_malformed_and_unapproved_values_fail_without_starting_agent(self):
        valid={"default_agent":"python-backend",
               "agent":agent_configuration("python-backend")}
        bad=[
            ([], "python-backend"),
            ("malformed", "python-backend"),
            ({"default_agent":"build"}, "python-backend"),
            (valid,"plan"),
            ({"default_agent":"python-backend","agent":[]}, "python-backend"),
            ({"default_agent":"python-backend",
              "agent":{"python-backend":{"mode":"primary"}}},"python-backend"),
            ({"default_agent":"python-backend",
              "agent":{"python-backend":{**valid["agent"]["python-backend"],
                       "prompt":"unreviewed role prompt"}}},"python-backend")
        ]
        for data,name in bad:
            with self.subTest(name=name,data=data), self.assertRaises(ValueError):
                validate_agent_config(data,name)

    def test_debug_list_shape_is_independent_of_config_validation(self):
        diagnostic=[{"info":"OpenCode v2 diagnostic array"}]
        self.assertIsInstance(json.loads(json.dumps(diagnostic)),list)
        with patch.dict(os.environ,{
            "OPENCODE_CONFIG_CONTENT":json.dumps({
                "default_agent":"python-backend",
                "agent":agent_configuration("python-backend")}),
            "FLEET_AGENT_ROLE":"python-backend",
        }):
            self.assertIsNone(main())

    def test_malformed_environment_is_not_silently_accepted(self):
        with patch.dict(os.environ,{
            "OPENCODE_CONFIG_CONTENT":"[]",
            "FLEET_AGENT_ROLE":"python-backend",
        }):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main()
