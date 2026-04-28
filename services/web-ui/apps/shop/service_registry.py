import time
from urllib.parse import quote

import requests
from django.conf import settings


_CACHE_TTL_SECONDS = 5
_service_cache: dict[str, tuple[float, str]] = {}
_health_cache: dict[str, tuple[float, dict]] = {}


def _from_cache(service_name: str) -> str | None:
    cached = _service_cache.get(service_name)
    if not cached:
        return None
    expires_at, url = cached
    if expires_at < time.time():
        _service_cache.pop(service_name, None)
        return None
    return url


def _save_cache(service_name: str, url: str) -> str:
    _service_cache[service_name] = (time.time() + _CACHE_TTL_SECONDS, url)
    return url


def _from_health_cache(cache_key: str) -> dict | None:
    cached = _health_cache.get(cache_key)
    if not cached:
        return None
    expires_at, payload = cached
    if expires_at < time.time():
        _health_cache.pop(cache_key, None)
        return None
    return payload


def _save_health_cache(cache_key: str, payload: dict) -> dict:
    _health_cache[cache_key] = (time.time() + _CACHE_TTL_SECONDS, payload)
    return payload


def resolve_service_url(service_name: str, fallback_url: str) -> str:
    cached_url = _from_cache(service_name)
    if cached_url:
        return cached_url

    consul_addr = getattr(settings, "CONSUL_HTTP_ADDR", "").rstrip("/")
    if not consul_addr:
        return fallback_url.rstrip("/")

    try:
        response = requests.get(
            f"{consul_addr}/v1/health/service/{quote(service_name)}",
            params={"passing": "true"},
            timeout=2,
        )
        response.raise_for_status()
        services = response.json()
    except requests.RequestException:
        return fallback_url.rstrip("/")

    for entry in services:
        service = entry.get("Service") or {}
        address = service.get("Address")
        port = service.get("Port")
        if address and port:
            return _save_cache(service_name, f"http://{address}:{port}")

    return fallback_url.rstrip("/")


def get_service_status(service_name: str, fallback_url: str, label: str) -> dict:
    cache_key = f"{service_name}:{fallback_url}"
    cached_status = _from_health_cache(cache_key)
    if cached_status:
        return cached_status

    base_url = resolve_service_url(service_name, fallback_url).rstrip("/")
    status_payload = {
        "name": service_name,
        "label": label,
        "base_url": base_url,
        "health_url": f"{base_url}/health/",
        "available": False,
    }

    try:
        response = requests.get(status_payload["health_url"], timeout=2)
        response.raise_for_status()
        payload = response.json()
        status_payload["available"] = payload.get("status") == "ok"
    except (requests.RequestException, ValueError):
        status_payload["available"] = False

    return _save_health_cache(cache_key, status_payload)
