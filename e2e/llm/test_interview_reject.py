"""Weak-answer prescan → REJECT path.

Sends deliberately evasive, off-topic answers and verifies the session
completes with a low overall score and the application status moves to
``rejected``.

Score threshold is <5 on a 1–10 scale — generous enough to survive minor
prompt tweaks while still catching any regression where the AI gives
passing scores to candidates who say "I don't know" to everything.
"""

from __future__ import annotations

import pytest

from helpers.api_client import ApiClient
from helpers.factories import submit_application
from llm.conftest import chat_to_completion

pytestmark = [pytest.mark.llm, pytest.mark.api]


WEAK_ANSWERS = [
    "ok",
    "I don't know.",
    "I have no experience with that.",
    "idk honestly",
    "no idea",
    "pass",
    "I haven't done anything like that.",
]


def test_weak_prescan_yields_rejection(
    api: ApiClient,
    persistent_admin_api: ApiClient,
    rich_published_vacancy,
):
    vacancy_id = rich_published_vacancy["id"]

    api.clear_token()
    application = submit_application(api, vacancy_id)
    token = application["prescan_token"]
    application_id = application["id"]

    try:
        final = chat_to_completion(
            api,
            token,
            WEAK_ANSWERS,
            filler="I really don't know. You can end the interview.",
        )
    except AssertionError as exc:
        history = api.get(f"/public/interview/{token}/chat/history/")
        raise AssertionError(
            f"Interview drive failed: {exc}\n"
            f"Chat history ({history.status}): {history.text()[:2000]}"
        ) from exc

    assert final["status"] == "completed", f"Not completed: {final!r}"

    hr_detail = persistent_admin_api.get(f"/hr/candidates/{application_id}/interview/")
    assert hr_detail.status == 200, f"HR detail lookup failed: {hr_detail.text()}"
    detail = hr_detail.json()

    overall = detail.get("overall_score")
    assert overall is not None, f"overall_score missing: {detail!r}"
    assert float(overall) < 5, (
        f"Expected overall_score < 5 for weak answers, got {overall}. "
        f"Replies: {final.get('_ai_replies')!r}"
    )

    # Application status should move to 'rejected' on this path
    hr_list = persistent_admin_api.get(f"/hr/vacancies/{vacancy_id}/candidates/")
    assert hr_list.status == 200
    apps = hr_list.json()
    mine = next((a for a in apps if a["id"] == application_id), None)
    assert mine is not None, f"Application not found: {apps!r}"
    assert mine["status"] == "rejected", (
        f"Expected 'rejected', got {mine['status']!r}. overall={overall} "
        f"summary={detail.get('ai_summary')!r}"
    )
