from typing import Any

import requests
from django.conf import settings

from .service_registry import resolve_service_url


def _headers(token: str | None) -> dict[str, str]:
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _auth_base_url() -> str:
    return resolve_service_url(settings.AUTH_SERVICE_NAME, settings.AUTH_INTERNAL_URL)


def _api_base_url() -> str:
    return resolve_service_url(settings.API_SERVICE_NAME, settings.API_INTERNAL_URL)


def auth_token(*, email: str, password: str) -> dict[str, Any]:
    url = f"{_auth_base_url().rstrip('/')}/api/token/"
    r = requests.post(url, json={"email": email, "password": password}, timeout=15)
    r.raise_for_status()
    return r.json()


def auth_get(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{_auth_base_url().rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.get(url, headers=_headers(token), params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def api_get(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{_api_base_url().rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.get(url, headers=_headers(token), params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def api_post(path: str, token: str, payload: dict | None = None) -> Any:
    url = f"{_api_base_url().rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.post(url, json=payload or {}, headers=_headers(token), timeout=30)
    r.raise_for_status()
    if r.text.strip():
        return r.json()
    return None


def auth_register(email: str, password: str, first_name: str, role: str = "PRO") -> Any:
    url = f"{_auth_base_url().rstrip('/')}/api/users/register/"
    r = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "role": role,
        },
        timeout=30,
    )
    r.raise_for_status()
    if r.text.strip():
        return r.json()
    return None


def api_patch(path: str, token: str, payload: dict | None = None) -> Any:
    url = f"{_api_base_url().rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.patch(url, json=payload or {}, headers=_headers(token), timeout=30)
    r.raise_for_status()
    if r.text.strip():
        return r.json()
    return None


def api_delete(path: str, token: str) -> Any:
    url = f"{_api_base_url().rstrip('/')}/api/{path.lstrip('/')}"
    r = requests.delete(url, headers=_headers(token), timeout=30)
    r.raise_for_status()
    if r.text.strip():
        return r.json()
    return None
