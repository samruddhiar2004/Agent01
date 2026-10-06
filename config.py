"""
Configuration settings for Agent01.
Centralizes environment settings, URLs, model names, thresholds, and n8n webhook parameters.
"""

# Ollama Local LLM Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:latest"
REQUEST_TIMEOUT = 60  # seconds to wait for model response

# Automation Thresholds & File Paths
THRESHOLD = 30
DATASET_PATH = "data/sample_employees.csv"
OUTPUT_REPORT_PATH = "output/employee_report.xlsx"

# n8n Integration Configuration
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/employee-threshold-reached"
N8N_REQUEST_TIMEOUT = 5  # seconds to wait for n8n response
