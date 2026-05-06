from __future__ import annotations

import requests
from django.conf import settings

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource

HH_CLIENT_ID_SETTINGS = {
    ParsedVacancySource.Type.HH_RU: "HH_RU_CLIENT_ID",
    ParsedVacancySource.Type.HH_UZ: "HH_UZ_CLIENT_ID",
}

HH_CLIENT_SECRET_SETTINGS = {
    ParsedVacancySource.Type.HH_RU: "HH_RU_CLIENT_SECRET",
    ParsedVacancySource.Type.HH_UZ: "HH_UZ_CLIENT_SECRET",
}


def request_hh_application_access_token(*, source_type: str) -> str:
    client_id, client_secret = _hh_client_credentials(source_type=source_type)
    if not client_id or not client_secret:
        raise ApplicationError("HeadHunter client credentials are not configured.")

    try:
        response = requests.post(
            getattr(settings, "HH_TOKEN_URL", "https://api.hh.ru/token"),
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", None)
        body = (getattr(exc.response, "text", "") or "")[:300]
        detail = "HeadHunter application token request failed"
        if status:
            detail = f"{detail}: HTTP {status}"
        if body:
            detail = f"{detail} - {body}"
        raise ApplicationError(detail) from exc

    access_token = response.json().get("access_token")
    if not access_token:
        raise ApplicationError("HeadHunter application token response did not include access_token.")
    return str(access_token)


def _hh_client_credentials(*, source_type: str) -> tuple[str, str]:
    client_id_setting = HH_CLIENT_ID_SETTINGS.get(source_type, "")
    client_secret_setting = HH_CLIENT_SECRET_SETTINGS.get(source_type, "")
    client_id = getattr(settings, client_id_setting, "") if client_id_setting else ""
    client_secret = getattr(settings, client_secret_setting, "") if client_secret_setting else ""
    return (
        client_id or getattr(settings, "HH_CLIENT_ID", ""),
        client_secret or getattr(settings, "HH_CLIENT_SECRET", ""),
    )
