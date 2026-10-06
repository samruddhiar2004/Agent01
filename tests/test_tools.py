"""
tests/test_tools.py - Unit tests for Agent01 tools and registry.
"""

import os
import unittest
from tools.dataset_tool import read_dataset, count_records
from tools.file_tool import check_file_exists, get_file_info
from tools.excel_tool import generate_excel_report
from tools.n8n_tool import trigger_n8n_webhook
from agent.tool_registry import ToolRegistry


class TestAgentTools(unittest.TestCase):

    def test_count_records(self):
        count = count_records("data/sample_employees.csv")
        self.assertEqual(count, 32)

    def test_read_dataset(self):
        records = read_dataset("data/sample_employees.csv")
        self.assertEqual(len(records), 32)
        self.assertIn("name", records[0])
        self.assertIn("department", records[0])

    def test_file_exists_and_info(self):
        exists = check_file_exists("data/sample_employees.csv")
        self.assertTrue(exists)

        info = get_file_info("data/sample_employees.csv")
        self.assertTrue(info["exists"])
        self.assertGreater(info["size_bytes"], 0)

    def test_generate_excel_report(self):
        test_out = "output/test_report.xlsx"
        result = generate_excel_report("data/sample_employees.csv", test_out)
        self.assertTrue(result["success"])
        self.assertEqual(result["records_written"], 32)
        self.assertTrue(os.path.exists(test_out))
        if os.path.exists(test_out):
            os.remove(test_out)

    def test_n8n_offline_handling(self):
        # When n8n is not running, the tool must not crash but return clear status
        result = trigger_n8n_webhook({"test": "data"}, webhook_url="http://localhost:5678/webhook/nonexistent")
        self.assertFalse(result["success"])
        self.assertIn(result["status"], ["unavailable", "timeout", "http_error"])

    def test_tool_registry(self):
        registry = ToolRegistry()
        registry.register("count", "Count records", count_records, {"file_path": "str"})
        self.assertTrue(registry.has_tool("count"))
        res = registry.execute("count", file_path="data/sample_employees.csv")
        self.assertEqual(res, 32)

        # Missing tool handling
        err_res = registry.execute("unknown_tool")
        self.assertIn("Error: Tool 'unknown_tool' is not registered", err_res)


if __name__ == "__main__":
    unittest.main()
