from __future__ import annotations

import sys
from hashlib import sha256

from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response

CACHE_TTL_SECONDS = 120
_NAMESPACE_VERSION_PREFIX = "api_cache_ns_ver:"
_PAYLOAD_PREFIX = "api_cache_payload:"


def _cache_enabled() -> bool:
    if 'test' in sys.argv:
        return False
    return bool(getattr(settings, 'API_RESPONSE_CACHE_ENABLED', not settings.DEBUG))


def _namespace_version_key(namespace: str) -> str:
    return f"{_NAMESPACE_VERSION_PREFIX}{namespace}"


def _get_namespace_version(namespace: str) -> int:
    key = _namespace_version_key(namespace)
    version = cache.get(key)
    if version is None:
        cache.set(key, 1, None)
        return 1
    return int(version)


def _build_payload_key(request, namespace: str) -> str:
    version = _get_namespace_version(namespace)
    fingerprint = sha256(request.get_full_path().encode("utf-8")).hexdigest()
    return f"{_PAYLOAD_PREFIX}{namespace}:v{version}:{fingerprint}"


def get_cached_response(request, namespace: str):
    if not _cache_enabled():
        return None

    user = getattr(request, "user", None)
    if request.method != "GET" or (user and user.is_authenticated):
        return None

    key = _build_payload_key(request, namespace)
    cached = cache.get(key)
    if cached is None:
        return None

    return Response(cached["data"], status=cached["status"])


def set_cached_response(request, namespace: str, response: Response, timeout: int = CACHE_TTL_SECONDS):
    if not _cache_enabled():
        return

    user = getattr(request, "user", None)
    if request.method != "GET" or (user and user.is_authenticated):
        return
    if response.status_code != 200:
        return

    key = _build_payload_key(request, namespace)
    cache.set(
        key,
        {
            "status": response.status_code,
            "data": response.data,
        },
        timeout,
    )


def invalidate_namespace(namespace: str):
    if not _cache_enabled():
        return

    key = _namespace_version_key(namespace)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, None)
