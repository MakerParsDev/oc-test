"""Offline proof that exhausted telemetry never interrupts the agent stdout pipe."""
import json
import unittest
from unittest.mock import patch

import oc_fleet_telemetry as telemetry


class MeasuredSource:
    def __init__(self, size):
        self.size = size
        self.read_count = 0

    def __iter__(self):
        for _ in range(self.size):
            self.read_count += 1
            yield (json.dumps({"type": "tool_use", "part": {
                "tool": "read", "state": {"status": "completed",
                "input": {"sensitive_data": "DO_NOT_LEAK"}}}}) + "\n").encode()


class TelemetryBudgetTest(unittest.TestCase):
    def test_cap_drains_entire_open_code_stream_without_network(self):
        source = MeasuredSource(7)
        stats = {}
        with patch.object(telemetry, "MAX_EVENTS", 3):
            count = telemetry.forward(source, run_id="123456", attempt="1",
                                      endpoint="", stats=stats)
        self.assertEqual(count, 3)
        self.assertEqual(source.read_count, 7)
        self.assertEqual(stats["lines"], 7)
        self.assertEqual(stats["accepted"], 3)
        self.assertEqual(stats["sent"], 0)

    def test_event_cap_preserves_order_and_sanitization(self):
        source = MeasuredSource(7)
        sent = []
        def sender(endpoint, audience, batch):
            sent.extend(dict(item) for item in batch)
        with patch.object(telemetry, "MAX_EVENTS", 3):
            count = telemetry.forward(source, run_id="123456", attempt="1",
                                      endpoint="https://example.invalid/ingest",
                                      sender=sender)
        self.assertEqual(count, 3)
        self.assertEqual(source.read_count, 7)
        self.assertEqual([event["seq"] for event in sent], [1, 2, 3])
        self.assertTrue(all(event["kind"] == "tool_use" for event in sent))
        self.assertNotIn("DO_NOT_LEAK", json.dumps(sent))


if __name__ == "__main__":
    unittest.main()
