"""
mock_n8n.py - Local n8n Webhook Service Simulator.

Runs a lightweight HTTP server on port 5678 to simulate n8n receiving
the webhook trigger from Agent01.
"""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import config


class N8nWebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Check if the requested path matches the configured webhook path
        expected_path = "/webhook/employee-threshold-reached"
        if self.path.startswith(expected_path):
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode("utf-8")) if post_data else {}
            except json.JSONDecodeError:
                payload = {"raw": post_data.decode("utf-8")}

            print("\n" + "=" * 65)
            print("[n8n WORKFLOW SERVICE] Webhook Trigger Received!")
            print(f"[n8n WORKFLOW SERVICE] Path:    {self.path}")
            print(f"[n8n WORKFLOW SERVICE] Payload: {json.dumps(payload, indent=2)}")
            print("[n8n WORKFLOW SERVICE] Action:  Starting downstream employee alert workflow...")
            print("=" * 65 + "\n")

            # Return HTTP 200 OK with success payload
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "success": True,
                "workflow_id": "wf_employee_threshold_v1",
                "status": "workflow_started",
                "message": "n8n workflow triggered successfully by Agent01."
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Webhook endpoint not found"}')

    def log_message(self, format, *args):
        # Suppress default server log lines to keep terminal clean
        return


def start_server(port: int = 5678):
    server = HTTPServer(("localhost", port), N8nWebhookHandler)
    print("=" * 65)
    print(f"n8n Mock Webhook Server is RUNNING on http://localhost:{port}")
    print(f"Listening for triggers at: {config.N8N_WEBHOOK_URL}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 65)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping n8n server...")
        server.server_close()


if __name__ == "__main__":
    start_server()
