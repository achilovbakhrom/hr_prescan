from __future__ import annotations

import logging
import os
import threading
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:  # pragma: no cover
    from geoip2.database import Reader
    from rest_framework.request import Request

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "ru", "uz")
DEFAULT_LANGUAGE = "en"

COUNTRY_TO_LANGUAGE: dict[str, str] = {
    "UZ": "uz",
    "RU": "ru",
    "BY": "ru",
    "KZ": "ru",
    "KG": "ru",
    "TJ": "ru",
    "UA": "ru",
}

_reader: Reader | None = None
_reader_lock = threading.Lock()


def _get_reader() -> Reader | None:
    global _reader
    if _reader is not None:
        return _reader

    db_path = getattr(settings, "GEOIP2_DB_PATH", "")
    if not db_path or not os.path.exists(db_path):
        return None

    with _reader_lock:
        if _reader is None:
            try:
                from geoip2.database import Reader

                _reader = Reader(db_path)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to open GeoIP2 DB at %s", db_path)
                return None
    return _reader


def _client_ip(request: Request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR") or ""
    if xff:
        return xff.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def _from_accept_language(request: Request) -> str | None:
    header = request.META.get("HTTP_ACCEPT_LANGUAGE") or ""
    for entry in header.split(","):
        code = entry.split(";")[0].strip().lower().split("-")[0]
        if code in SUPPORTED_LANGUAGES:
            return code
    return None


def _from_ip(request: Request) -> str | None:
    ip = _client_ip(request)
    if not ip:
        return None
    reader = _get_reader()
    if reader is None:
        return None
    try:
        response = reader.country(ip)
    except Exception:  # noqa: BLE001
        return None
    country_code = (response.country.iso_code or "").upper()
    return COUNTRY_TO_LANGUAGE.get(country_code)


def detect_language(request: Request) -> str:
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        pref = getattr(user, "language", None)
        if pref in SUPPORTED_LANGUAGES:
            return pref

    return (
        _from_accept_language(request)
        or _from_ip(request)
        or DEFAULT_LANGUAGE
    )
