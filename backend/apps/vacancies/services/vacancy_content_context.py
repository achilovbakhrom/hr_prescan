from typing import Any


def merge_with_current_content(content: dict[str, str], current_content: dict[str, str]) -> dict[str, str]:
    return {
        "description": content.get("description", "").strip() or current_content["description"],
        "requirements": content.get("requirements", "").strip() or current_content["requirements"],
        "responsibilities": content.get("responsibilities", "").strip() or current_content["responsibilities"],
    }


def response_payload(*, content: dict[str, str], context: dict[str, Any]) -> dict[str, Any]:
    return {
        **content,
        "generation_context": {
            "turns": [
                *context["generation_context"].get("turns", []),
                {
                    "instruction": context["additional_instruction"],
                    "content": content,
                },
            ][-5:],
        },
    }


def clean_generation_context(raw_context: dict[str, Any]) -> dict[str, Any]:
    raw_turns = raw_context.get("turns")
    if not isinstance(raw_turns, list):
        return {"turns": []}

    turns = []
    for raw_turn in raw_turns[-5:]:
        if not isinstance(raw_turn, dict):
            continue
        raw_content = raw_turn.get("content")
        if not isinstance(raw_content, dict):
            raw_content = {}
        turns.append(
            {
                "instruction": str(raw_turn.get("instruction") or "")[:1000],
                "content": {
                    "description": str(raw_content.get("description") or "")[:3000],
                    "requirements": str(raw_content.get("requirements") or "")[:2000],
                    "responsibilities": str(raw_content.get("responsibilities") or "")[:2000],
                },
            }
        )
    return {"turns": turns}
