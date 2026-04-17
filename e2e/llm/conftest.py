"""LLM test fixtures and helpers — opt-in, slow, hit real AI APIs.

These helpers drive the prescan chat interview to completion by posting
scripted candidate answers and polling the public interview endpoint until
the session transitions to COMPLETED (or a hard timeout).

Why long timeouts: each AI turn round-trips Gemini (sometimes 5–15s per
response), and the full interview typically runs 5–7 turns. 5 min is a
comfortable ceiling; real runs finish in 60–90s.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient


# Hard caps for interview-drive helpers. Interview rounds are bounded by the
# AI prompt (typically 5–7 Q/A turns), so per-turn + overall timeouts keep
# runaway loops bounded without being flaky.
PER_TURN_TIMEOUT = 60.0       # max seconds to wait for one AI reply
OVERALL_TIMEOUT = 300.0       # max seconds for a full interview
POLL_INTERVAL = 2.0           # seconds between status polls
MAX_EXTRA_TURNS = 6           # extra nudge turns after scripted answers exhausted


class InterviewDriveError(AssertionError):
    """Raised when interview drive fails; re-raise includes captured context."""


def _send_with_retry(api: ApiClient, token: str, message: str) -> dict[str, Any]:
    """POST one candidate message, return parsed response. Raises on 5xx."""
    start = time.monotonic()
    last_err: str | None = None
    while time.monotonic() - start < PER_TURN_TIMEOUT:
        resp = api.post(
            f"/public/interview/{token}/chat/",
            data={"message": message},
        )
        if resp.status == 200:
            return resp.json()
        last_err = f"status={resp.status} body={resp.text()[:500]}"
        # 400 means interview already completed — surface that to caller.
        if resp.status == 400:
            return {"_completed": True, "_body": resp.text()}
        time.sleep(POLL_INTERVAL)
    raise InterviewDriveError(f"Chat post timed out: {last_err}")


def _poll_until_completed(api: ApiClient, token: str, deadline: float) -> dict[str, Any]:
    """GET the interview detail until status == completed or deadline passes."""
    last_body: dict[str, Any] = {}
    while time.monotonic() < deadline:
        resp = api.get(f"/public/interview/{token}/")
        if resp.status == 200:
            last_body = resp.json()
            if last_body.get("status") == "completed":
                return last_body
        time.sleep(POLL_INTERVAL)
    raise InterviewDriveError(
        f"Interview did not complete within {OVERALL_TIMEOUT}s. "
        f"Last status={last_body.get('status')!r}. Last body: {last_body!r}"
    )


def chat_to_completion(
    api: ApiClient,
    token: str,
    answers: list[str],
    *,
    filler: str = "I don't have more to add, please wrap up.",
) -> dict[str, Any]:
    """Drive a prescan chat to completion using scripted `answers`.

    Starts the session, then sends each scripted answer. If the AI keeps
    asking questions beyond our script, falls back to `filler` for up to
    MAX_EXTRA_TURNS more turns. Finally polls the detail endpoint until
    status == "completed".

    Returns the final public interview payload. Captures AI replies in
    ``result["_ai_replies"]`` for debug assertions.
    """
    start = api.post(f"/public/interview/{token}/start/")
    assert start.status == 200, f"start failed: {start.text()}"

    ai_replies: list[str] = []
    deadline = time.monotonic() + OVERALL_TIMEOUT
    completed = False

    for answer in answers:
        if time.monotonic() >= deadline:
            break
        reply = _send_with_retry(api, token, answer)
        if reply.get("_completed"):
            completed = True
            break
        text = reply.get("text", "")
        ai_replies.append(text)
        if "[INTERVIEW_COMPLETE]" in text:
            completed = True
            break

    # If AI still wants more turns, send a few filler messages so it can wrap
    extra = 0
    while not completed and extra < MAX_EXTRA_TURNS and time.monotonic() < deadline:
        reply = _send_with_retry(api, token, filler)
        if reply.get("_completed"):
            completed = True
            break
        text = reply.get("text", "")
        ai_replies.append(text)
        if "[INTERVIEW_COMPLETE]" in text:
            completed = True
            break
        extra += 1

    final = _poll_until_completed(api, token, deadline)
    final["_ai_replies"] = ai_replies
    return final


def _create_rich_vacancy(admin_api: ApiClient, *, language: str = "en") -> dict[str, Any]:
    """Create a published vacancy with 3 questions, 2 criteria, given language."""
    resp = admin_api.post("/hr/vacancies/", data={
        "title": f"E2E LLM Vacancy {uuid.uuid4().hex[:6]}",
        "description": "Mid-level Python/Django backend engineer. "
                       "You will build REST APIs, work with Postgres, and ship "
                       "production code on a small team.",
        "requirements": "3+ years Python, Django, Postgres, REST APIs, Git",
        "skills": ["python", "django", "postgres"],
        "experience_level": "middle",
        "employment_type": "full_time",
        "location": "Remote",
        "is_remote": True,
        "prescanning_language": language,
    })
    assert resp.status == 201, f"Create vacancy failed: {resp.text()}"
    vacancy = resp.json()
    vid = vacancy["id"]
    register_vacancy_for_cleanup(admin_api, vid)

    questions = [
        ("Describe a recent Python/Django project you shipped.", "Hard Skill"),
        ("Tell me about a time you disagreed with a teammate — how did you handle it?", "Soft Skill"),
        ("How do you decide when a feature is 'done' and ready to ship?", "Behavioral"),
    ]
    for text, category in questions:
        r = admin_api.post(f"/hr/vacancies/{vid}/questions/", data={
            "text": text, "category": category, "step": "prescanning",
        })
        assert r.status == 201, f"Add question failed: {r.text()}"

    criteria = [
        ("Python fluency", "Depth of hands-on Python and Django knowledge"),
        ("Communication", "Clarity and structure when explaining technical work"),
    ]
    for name, desc in criteria:
        r = admin_api.post(f"/hr/vacancies/{vid}/criteria/", data={
            "name": name, "description": desc, "weight": 3, "step": "prescanning",
        })
        assert r.status == 201, f"Add criteria failed: {r.text()}"

    publish = admin_api.patch(f"/hr/vacancies/{vid}/status/", data={"action": "publish"})
    assert publish.status == 200, f"Publish failed: {publish.text()}"

    return admin_api.get(f"/hr/vacancies/{vid}/").json()


@pytest.fixture()
def rich_published_vacancy(persistent_admin_api: ApiClient) -> dict[str, Any]:
    """Published vacancy with 3 questions, 2 custom criteria, English language."""
    return _create_rich_vacancy(persistent_admin_api, language="en")


@pytest.fixture()
def russian_published_vacancy(persistent_admin_api: ApiClient) -> dict[str, Any]:
    """Published vacancy configured for Russian prescanning."""
    return _create_rich_vacancy(persistent_admin_api, language="ru")
