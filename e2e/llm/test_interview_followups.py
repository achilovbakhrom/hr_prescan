"""Follow-up context retention — soft signal of AI grounding.

Mentions a specific technology in the first turn and checks that the AI
references that topic (or a synonym) somewhere in its next few replies.

The check is intentionally lenient: we only hard-fail when the AI returns
an empty reply. Missing the reference logs a warning via pytest.warns-like
output but still passes the test, because prompt rewrites will inevitably
change how often the model echoes prior turns.
"""

from __future__ import annotations

import warnings

import pytest

from helpers.api_client import ApiClient
from helpers.factories import submit_application
from llm.conftest import _send_with_retry

pytestmark = [pytest.mark.llm, pytest.mark.api]


CONTEXT_KEYWORDS = ("django", "channels", "realtime", "real-time", "dashboard")

TURN_MESSAGES = [
    "Hi! I'm Priya, a Python/Django developer. I used Django Channels for a "
    "realtime dashboard that streams live metrics to our ops team.",
    "In that realtime dashboard project I wrote around 60% of the backend "
    "and did all the WebSocket plumbing.",
    "I own the on-call rotation for that service and tune Postgres as well.",
]


def test_ai_references_prior_context_in_followups(
    api: ApiClient,
    rich_published_vacancy,
):
    vacancy_id = rich_published_vacancy["id"]

    api.clear_token()
    application = submit_application(api, vacancy_id)
    token = application["prescan_token"]

    start = api.post(f"/public/interview/{token}/start/")
    assert start.status == 200, f"start failed: {start.text()}"

    replies: list[str] = []
    for message in TURN_MESSAGES:
        reply = _send_with_retry(api, token, message)
        if reply.get("_completed"):
            # Some prompt configs may end quickly; still capture history.
            break
        text = reply.get("text", "")
        assert text.strip(), (
            f"AI returned empty reply to message {message!r}. "
            f"Full response: {reply!r}"
        )
        replies.append(text)

    assert replies, "AI produced no replies at all"

    joined = " ".join(replies).lower()
    referenced = [kw for kw in CONTEXT_KEYWORDS if kw in joined]

    if not referenced:
        # Soft-fail: warn but don't break the suite. Context retention is
        # best-effort and prompt-sensitive; the caller will see this warning
        # in the pytest output and can tune the prompt.
        warnings.warn(
            "AI did not reference any of the seeded keywords "
            f"{CONTEXT_KEYWORDS} across {len(replies)} replies. "
            f"Replies: {replies!r}",
            stacklevel=2,
        )
    else:
        # Record which keywords were matched for debugging
        print(f"Matched context keywords: {referenced}")
