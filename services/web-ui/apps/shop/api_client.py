from typing import Any

import requests
from django.conf import settings


def _headers(token: str | None) -> dict[str, str]:
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def auth_token(*, email: str, password: str) -> dict[str, Any]:
    url = f"{settings.AUTH_INTERNAL_URL.rstrip('/')}/api/token/"
    r = requests.post(url, json={"email": email, "password": password}, timeout=15)
    r.raise_for_status()
    return r.json()


def api_get(path: str, token: str) -> Any:
    url = f"{settings.API_INTERNAL_URL.rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.get(url, headers=_headers(token), timeout=20)
    r.raise_for_status()
    return r.json()


def api_post(endpoint, token=None, data=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{settings.AUTH_INTERNAL_URL}/api/{endpoint}"  # ou API_INTERNAL_URL selon votre config
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()