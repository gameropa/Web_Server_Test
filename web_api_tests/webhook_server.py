#!/usr/bin/env python3
"""
Simple webhook server for auto-deploying on git push.
Run this on your deployment server.
"""
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import hmac
import hashlib

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key")
REPO_PATH = os.getenv("REPO_PATH", "/opt/web-api-tests")
COMPOSE_FILE = os.getenv("COMPOSE_FILE", "docker-compose-rpi.yml")


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Verify GitHub signature
        signature = self.headers.get("X-Hub-Signature-256", "")
        if signature:
            expected = (
                "sha256="
                + hmac.new(
                    WEBHOOK_SECRET.encode(), body, hashlib.sha256
                ).hexdigest()
            )
            if not hmac.compare_digest(signature, expected):
                self.send_response(401)
                self.end_headers()
                self.log_message("Webhook signature verification failed")
                return

        try:
            payload = json.loads(body)
            if payload.get("ref") == "refs/heads/main":
                self.send_response(200)
                self.end_headers()
                self.deploy()
            else:
                self.send_response(202)
                self.end_headers()
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.log_message(f"Error: {e}")

    def deploy(self):
        """Pull latest code and redeploy with docker compose."""
        try:
            os.chdir(REPO_PATH)
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "pull"], check=True)
            subprocess.run(
                ["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"],
                check=True,
            )
            subprocess.run(["docker", "image", "prune", "-f"], check=True)
            self.log_message("Deployment successful")
        except subprocess.CalledProcessError as e:
            self.log_message(f"Deployment failed: {e}")

    def log_message(self, format, *args):
        """Override to log to stdout instead of stderr."""
        print(f"[{self.client_address[0]}] {format % args}")


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", 9000))
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"Webhook server listening on port {port}")
    print(f"Repository: {REPO_PATH}")
    print(f"Compose file: {COMPOSE_FILE}")
    print("Configure GitHub webhook to: http://your-server:9000/webhook")
    server.serve_forever()
