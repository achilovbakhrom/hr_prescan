import requests
from django.conf import settings

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource

HH_API_BASE_URLS = {
    ParsedVacancySource.Type.HH_RU: "https://api.hh.ru",
    ParsedVacancySource.Type.HH_UZ: "https://api.hh.uz",
}

HH_SITE_ACCESS_TOKEN_SETTINGS = {
    ParsedVacancySource.Type.HH_RU: "HH_RU_ACCESS_TOKEN",
    ParsedVacancySource.Type.HH_UZ: "HH_UZ_ACCESS_TOKEN",
}


def hh_get(*, source: ParsedVacancySource, path: str, params: dict) -> dict:
    base_url = HH_API_BASE_URLS[source.source_type]
    try:
        response = requests.get(
            f"{base_url}{path}",
            params=params,
            headers=_hh_headers(source=source),
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", None)
        body = (getattr(exc.response, "text", "") or "")[:300]
        detail = "HeadHunter API request failed"
        if status:
            detail = f"{detail}: HTTP {status}"
        if body:
            detail = f"{detail} - {body}"
        raise ApplicationError(detail) from exc
    return response.json()


def _hh_headers(*, source: ParsedVacancySource) -> dict[str, str]:
    user_agent = getattr(settings, "HH_USER_AGENT", "HR PreScreen vacancy parser")
    headers = {
        "Accept": "application/json",
        "User-Agent": user_agent,
        "HH-User-Agent": user_agent,
    }
    access_token = _hh_access_token(source=source)
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _hh_access_token(*, source: ParsedVacancySource) -> str:
    source_token = (source.settings or {}).get("access_token")
    if source_token:
        return str(source_token)
    site_setting = HH_SITE_ACCESS_TOKEN_SETTINGS.get(source.source_type, "")
    site_token = getattr(settings, site_setting, "") if site_setting else ""
    return site_token or getattr(settings, "HH_ACCESS_TOKEN", "")
