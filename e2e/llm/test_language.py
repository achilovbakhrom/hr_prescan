"""Language respect — Russian prescan starts in Russian.

Only checks the first AI turn to keep the test fast. We don't run to
completion because language adherence is visible immediately.
"""

from __future__ import annotations

import re

import pytest

from helpers.api_client import ApiClient
from helpers.factories import submit_application
from llm.conftest import _send_with_retry

pytestmark = [pytest.mark.llm, pytest.mark.api]


CYRILLIC = re.compile(r"[а-яА-ЯёЁ]")


def test_russian_vacancy_greets_in_russian(
    api: ApiClient,
    russian_published_vacancy,
):
    vacancy_id = russian_published_vacancy["id"]

    api.clear_token()
    application = submit_application(api, vacancy_id)
    token = application["prescan_token"]

    start = api.post(f"/public/interview/{token}/start/")
    assert start.status == 200, f"start failed: {start.text()}"

    reply = _send_with_retry(api, token, "Привет, меня зовут Иван.")
    assert not reply.get("_completed"), f"Unexpected early completion: {reply!r}"
    text = reply.get("text", "")
    assert text.strip(), f"Empty AI reply: {reply!r}"

    assert CYRILLIC.search(text), (
        "Expected Cyrillic characters in AI reply for a Russian-language "
        f"vacancy, got: {text!r}"
    )
