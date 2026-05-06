from unittest.mock import Mock, patch

import pytest
import requests
from django.test import override_settings

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource
from apps.job_parser.services.hh_auth import request_hh_application_access_token


@override_settings(
    HH_TOKEN_URL="https://api.hh.ru/token",
    HH_UZ_CLIENT_ID="client-id",
    HH_UZ_CLIENT_SECRET="client-secret",
)
def test_request_hh_application_access_token_uses_client_credentials():
    response = Mock()
    response.json.return_value = {"access_token": "app-token"}
    response.raise_for_status.return_value = None

    with patch("apps.job_parser.services.hh_auth.requests.post", return_value=response) as request_post:
        token = request_hh_application_access_token(source_type=ParsedVacancySource.Type.HH_UZ)

    assert token == "app-token"
    request_post.assert_called_once_with(
        "https://api.hh.ru/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "client-id",
            "client_secret": "client-secret",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )


@override_settings(HH_UZ_CLIENT_ID="", HH_UZ_CLIENT_SECRET="", HH_CLIENT_ID="", HH_CLIENT_SECRET="")
def test_request_hh_application_access_token_requires_credentials():
    with pytest.raises(ApplicationError, match="credentials"):
        request_hh_application_access_token(source_type=ParsedVacancySource.Type.HH_UZ)


@override_settings(HH_UZ_CLIENT_ID="client-id", HH_UZ_CLIENT_SECRET="client-secret")
def test_request_hh_application_access_token_reports_http_error():
    response = Mock()
    response.status_code = 403
    response.text = '{"error":"forbidden"}'
    response.raise_for_status.side_effect = requests.HTTPError(response=response)

    with (
        patch("apps.job_parser.services.hh_auth.requests.post", return_value=response),
        pytest.raises(ApplicationError, match="HTTP 403"),
    ):
        request_hh_application_access_token(source_type=ParsedVacancySource.Type.HH_UZ)
