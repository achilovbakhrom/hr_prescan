from unittest.mock import patch

from rest_framework.test import APIClient

from tests.factories import UserFactory


def test_hr_ai_assistant_accepts_long_vacancy_creation_text():
    user = UserFactory(role="admin")
    message = ("Create a vacancy from this job description:\n" + ("Backend engineer responsibilities. " * 120)).strip()

    client = APIClient()
    client.force_authenticate(user=user)
    with patch(
        "apps.common.apis_ai.process_ai_command",
        return_value={"success": True, "message": "Draft created.", "actions": []},
    ) as process_mock:
        response = client.post(
            "/api/hr/ai-assistant/",
            {"message": message, "context": {}},
            format="json",
        )

    assert response.status_code == 200
    process_mock.assert_called_once()
    assert process_mock.call_args.kwargs["message"] == message
