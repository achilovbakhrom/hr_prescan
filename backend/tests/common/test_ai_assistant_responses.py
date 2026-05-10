from apps.common.ai_assistant.agent import _build_final_response as build_hr_response
from apps.common.candidate_ai_assistant.agent import _build_final_response as build_candidate_response


def test_hr_assistant_clarification_is_not_reported_as_action_error():
    response = build_hr_response(
        gpt_message="Which company should I use?",
        actions_taken=[
            {
                "tool": "create_vacancy",
                "result": {
                    "success": False,
                    "action": "clarify",
                    "message": "Multiple companies match. Please choose one.",
                },
            }
        ],
    )

    assert response["success"] is True
    assert response["message"] == "Which company should I use?"


def test_hr_assistant_sanitizes_raw_translation_error():
    response = build_hr_response(
        gpt_message="I could not complete that.",
        actions_taken=[
            {
                "tool": "translate_content",
                "result": {"success": False, "message": "has no translation"},
            }
        ],
    )

    assert response["success"] is False
    assert "has no translation" not in response["message"]
    assert "Translation is not available for that content yet." in response["message"]


def test_candidate_assistant_clarification_is_not_reported_as_action_error():
    response = build_candidate_response(
        gpt_message="Please add your job title first.",
        actions_taken=[
            {
                "tool": "build_my_cv",
                "result": {
                    "success": False,
                    "action": "clarify",
                    "message": "Job title is required.",
                },
            }
        ],
    )

    assert response["success"] is True
    assert response["message"] == "Please add your job title first."
