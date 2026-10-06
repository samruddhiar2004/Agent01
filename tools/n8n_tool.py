"""
tools/n8n_tool.py - n8n Workflow Automation Integration for Agent01.

Provides a tool to trigger external n8n workflows via webhook.
Agent01 maintains full responsibility for decision-making and conditions;
n8n is invoked purely as an external workflow executor.
"""

from typing import Dict, Any, Optional
import requests
import config


def trigger_n8n_webhook(
    event_data: Optional[Dict[str, Any]] = None,
    webhook_url: str = config.N8N_WEBHOOK_URL
) -> Dict[str, Any]:
    """
    Triggers an n8n webhook workflow with payload data.

    Args:
        event_data: Key-value data to send to the webhook (e.g. employee count, file path).
        webhook_url: The local or remote n8n webhook URL.

    Returns:
        Dictionary detailing the webhook trigger status.
    """
    payload = event_data or {
        "event": "threshold_reached",
        "threshold": config.THRESHOLD,
        "report_file": config.OUTPUT_REPORT_PATH
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=config.N8N_REQUEST_TIMEOUT
        )
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status": "unavailable",
            "message": (
                f"[n8n Unavailable] Could not connect to n8n at '{webhook_url}'. "
                f"Make sure n8n is running locally (e.g. 'n8n start' or docker) if you wish to trigger it."
            )
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status": "timeout",
            "message": f"[n8n Timeout] Webhook request to '{webhook_url}' timed out."
        }
    except requests.exceptions.RequestException as err:
        return {
            "success": False,
            "status": "error",
            "message": f"[n8n Error] Network exception when calling webhook: {err}"
        }

    if response.status_code in (200, 201):
        return {
            "success": True,
            "status": "triggered",
            "http_status": response.status_code,
            "message": f"Successfully triggered n8n webhook at '{webhook_url}'."
        }
    else:
        return {
            "success": False,
            "status": "http_error",
            "http_status": response.status_code,
            "message": f"n8n webhook returned HTTP {response.status_code}: {response.text}"
        }
