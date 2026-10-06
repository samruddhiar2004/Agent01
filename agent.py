"""
agent.py - Main entry point for Agent01.

Phase 6: Complete Agent Automation with n8n Integration.
Architecture:
  Python Agent -> Agent Orchestrator -> Ollama LLM (llama3.1) -> Local Tools -> n8n Workflow

Responsibilities:
  Agent01: Understands goal, monitors data, evaluates threshold, decides actions, verifies results.
  n8n: Receives trigger and executes external downstream workflows.
"""

import sys
import config
from agent import Agent, OllamaClient, ToolRegistry
from tools import (
    read_dataset,
    count_records,
    generate_excel_report,
    check_file_exists,
    get_file_info,
    trigger_n8n_webhook
)


def build_tool_registry() -> ToolRegistry:
    """Populates the ToolRegistry with all available agent tools."""
    registry = ToolRegistry()

    registry.register(
        name="count_records",
        description="Counts the total number of records (rows) in a CSV dataset file.",
        func=count_records,
        parameters_schema={"file_path": "string (path to CSV file, default is 'data/sample_employees.csv')"}
    )

    registry.register(
        name="read_dataset",
        description="Reads all rows from a CSV dataset file and returns them as records.",
        func=read_dataset,
        parameters_schema={"file_path": "string (path to CSV file, default is 'data/sample_employees.csv')"}
    )

    registry.register(
        name="generate_excel_report",
        description="Creates a styled Excel (.xlsx) workbook from a CSV dataset and saves it to output path.",
        func=generate_excel_report,
        parameters_schema={
            "source_file": "string (path to CSV dataset, default is 'data/sample_employees.csv')",
            "output_path": "string (path where Excel will be saved, default is 'output/employee_report.xlsx')"
        }
    )

    registry.register(
        name="get_file_info",
        description="Checks if a file exists on disk and returns its size and verification details.",
        func=get_file_info,
        parameters_schema={"file_path": "string (path to the file to inspect/verify)"}
    )

    registry.register(
        name="trigger_n8n_webhook",
        description="Triggers an external n8n workflow webhook on localhost with event summary data.",
        func=trigger_n8n_webhook,
        parameters_schema={"event_data": "dict (payload data such as employee count, report file path)"}
    )

    return registry


def run_agent(threshold: int = config.THRESHOLD) -> None:
    print("=" * 75)
    print("Agent01 - Autonomous Local AI Automation Agent")
    print(f"Target Model:       {config.OLLAMA_MODEL}")
    print(f"Configured Limit:   THRESHOLD = {threshold}")
    print(f"Dataset File:       {config.DATASET_PATH}")
    print(f"Output Report:      {config.OUTPUT_REPORT_PATH}")
    print(f"n8n Webhook:        {config.N8N_WEBHOOK_URL}")
    print("=" * 75)

    llm = OllamaClient()
    registry = build_tool_registry()
    agent = Agent(llm=llm, tool_registry=registry, max_steps=7)

    goal = (
        f"Monitor the employee dataset at '{config.DATASET_PATH}' and count the records. "
        f"If the count reaches or exceeds the threshold of {threshold}: "
        f"1. Generate an Excel report at '{config.OUTPUT_REPORT_PATH}'. "
        f"2. Verify that the file exists on disk. "
        f"3. Trigger the n8n webhook with the summary data. "
        f"If the threshold is NOT reached, do not generate the report or trigger n8n, and report why."
    )

    result = agent.run(goal=goal)

    print("=" * 75)
    print("Agent Execution Summary:")
    print(f"Success:      {result['success']}")
    print(f"Total Steps:  {result['steps']}")
    print(f"Summary:      {result.get('summary', 'None')}")
    print("=" * 75)


if __name__ == "__main__":
    threshold_arg = int(sys.argv[1]) if len(sys.argv) > 1 else config.THRESHOLD
    run_agent(threshold=threshold_arg)