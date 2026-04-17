"""Strong-answer prescan → ADVANCE path.

Drives the prescan interview with plausible answers from a Python/Django
engineer and verifies the session completes with a real score, per-criterion
scores, and a non-empty AI summary.

Assertions are intentionally structural (score range, non-empty summary)
rather than text-matching, so the test survives prompt-text drift.
"""

from __future__ import annotations

import pytest

from helpers.api_client import ApiClient
from helpers.factories import submit_application
from llm.conftest import chat_to_completion

pytestmark = [pytest.mark.llm, pytest.mark.api]


STRONG_ANSWERS = [
    "Hi, I'm Alex. I have about 5 years of Python experience, most of it "
    "with Django. Happy to walk you through my background.",
    "I recently shipped a Django REST API for a fintech dashboard: 40+ "
    "endpoints, Postgres with GIN indexes for search, Celery for background "
    "jobs, and Redis for caching. Handled about 200 req/s at peak.",
    "A teammate and I disagreed about using Celery vs. a simple cron. I "
    "wrote a short doc comparing both on reliability, retries, and ops "
    "cost. We walked through it together and landed on Celery for the "
    "retry semantics — staying evidence-driven kept it a good conversation.",
    "For me, 'done' means: tests cover the happy path and at least two "
    "edge cases, migrations reviewed, error logging in place, a runbook "
    "entry for on-call, and a feature flag if the change is risky.",
    "I care most about writing code that's easy for the next person to "
    "change. Small PRs, clear naming, tests that document intent. That's "
    "what I'd bring to the team.",
]


def test_strong_prescan_completes_with_advance_signals(
    api: ApiClient,
    persistent_admin_api: ApiClient,
    rich_published_vacancy,
):
    vacancy_id = rich_published_vacancy["id"]

    # Anonymous candidate applies
    api.clear_token()
    application = submit_application(api, vacancy_id)
    token = application["prescan_token"]
    application_id = application["id"]

    try:
        final = chat_to_completion(api, token, STRONG_ANSWERS)
    except AssertionError as exc:
        history = api.get(f"/public/interview/{token}/chat/history/")
        raise AssertionError(
            f"Interview drive failed: {exc}\n"
            f"Chat history ({history.status}): {history.text()[:2000]}"
        ) from exc

    assert final["status"] == "completed", f"Not completed: {final!r}"

    # The HR detail endpoint has the scoring payload the public view omits.
    # We need to look up the interview id via HR candidate detail.
    hr_detail = persistent_admin_api.get(f"/hr/candidates/{application_id}/interview/")
    assert hr_detail.status == 200, f"HR detail lookup failed: {hr_detail.text()}"
    detail = hr_detail.json()

    overall = detail.get("overall_score")
    assert overall is not None, f"overall_score missing: {detail!r}"
    assert 1 <= float(overall) <= 10, (
        f"overall_score out of range: {overall!r}. Replies: {final.get('_ai_replies')!r}"
    )

    summary = detail.get("ai_summary") or ""
    assert len(summary) > 20, f"ai_summary too short/empty: {summary!r}"

    scores = detail.get("scores") or []
    score_names = {s.get("criteria_name", "") for s in scores}
    # At least one score row per custom criterion we defined
    assert any("python" in n.lower() for n in score_names), (
        f"Expected a Python-fluency criterion score. Got: {score_names!r}"
    )
    assert any("communication" in n.lower() for n in score_names), (
        f"Expected a Communication criterion score. Got: {score_names!r}"
    )

    # /candidate/applications/ is only populated for logged-in, email-bound
    # candidates. We submitted anonymously, so verify via HR list instead:
    # the application status should have moved off "applied" toward the
    # advance lane once prescan completes.
    hr_list = persistent_admin_api.get(f"/hr/vacancies/{vacancy_id}/candidates/")
    assert hr_list.status == 200, f"HR list failed: {hr_list.text()}"
    apps = hr_list.json()
    mine = next((a for a in apps if a["id"] == application_id), None)
    assert mine is not None, f"Application not found in HR list: {apps!r}"
    # Strong answers should advance (prescanned/shortlisted) or at minimum
    # not stay stuck in 'applied'. We only assert it's not 'rejected'.
    assert mine["status"] != "rejected", (
        f"Strong answers produced 'rejected' status. overall={overall} "
        f"summary={summary!r}"
    )
