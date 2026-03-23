#!/usr/bin/env python3
"""Enregistre le service auprès de Consul (service discovery)."""
import os
import sys
import urllib.error
import urllib.request
import json

CONSUL = os.environ.get("CONSUL_HTTP_ADDR", "http://consul:8500").rstrip("/")
NAME = os.environ.get("SERVICE_NAME", "unknown")
PORT = int(os.environ.get("SERVICE_PORT", "8000"))
# Nom DNS résolu par les autres conteneurs sur le réseau Docker
ADDRESS = os.environ.get("SERVICE_ADDRESS", NAME)
CHECK_PATH = os.environ.get("CONSUL_CHECK_PATH", "/health/")
SERVICE_ID = os.environ.get("SERVICE_ID", f"{NAME}-1")

payload = {
    "ID": SERVICE_ID,
    "Name": NAME,
    "Tags": ["marketpharm", "django"],
    "Address": ADDRESS,
    "Port": PORT,
    "Check": {
        "HTTP": f"http://{ADDRESS}:{PORT}{CHECK_PATH}",
        "Interval": "15s",
        "Timeout": "5s",
        "DeregisterCriticalServiceAfter": "1m",
    },
}

url = f"{CONSUL}/v1/agent/service/register"
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="PUT",
)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status not in (200,):
            print(f"consul register unexpected status {resp.status}", file=sys.stderr)
            sys.exit(1)
except urllib.error.URLError as e:
    print(f"consul register failed: {e}", file=sys.stderr)
    sys.exit(1)
print(f"registered {NAME} at {ADDRESS}:{PORT} in consul")
