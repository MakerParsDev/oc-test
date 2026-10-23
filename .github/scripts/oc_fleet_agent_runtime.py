#!/usr/bin/env python3
"""Check the prepared OpenCode agent contract before any model invocation.

The CLI's `debug config` output is only diagnostics. Depending on the
installed version it may be a JSON list rather than a mapping; the reviewed,
deterministic OPENCODE_CONFIG_CONTENT is the actual trusted input here.
"""
import json
import os

from oc_fleet_contract import AGENTS, agent_configuration


def validate_agent_config(config, selected):
    if type(selected) is not str or selected not in AGENTS:
        raise ValueError("unapproved agent role")
    if type(config) is not dict or config.get("default_agent") != selected:
        raise ValueError("selected agent missing from generated configuration")
    if selected == "build":
        return
    agents = config.get("agent")
    prepared = agents.get(selected) if type(agents) is dict else None
    expected = agent_configuration(selected)[selected]
    if type(prepared) is not dict or any(
        prepared.get(field) != expected[field]
        for field in ("description", "mode", "prompt")
    ):
        raise ValueError("selected primary agent configuration mismatch")


def main():
    try:
        config = json.loads(os.environ["OPENCODE_CONFIG_CONTENT"])
        validate_agent_config(config, os.environ["FLEET_AGENT_ROLE"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit("Fleet agent configuration rejected: " + str(exc)) from None


if __name__ == "__main__":
    main()
