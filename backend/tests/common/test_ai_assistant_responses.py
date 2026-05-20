from apps.accounts.models import User
from apps.common.ai_assistant.agent import _build_final_response as build_hr_response
from apps.common.ai_assistant.tools import execute_tool
from apps.common.candidate_ai_assistant.agent import _build_final_response as build_candidate_response
from apps.notifications.models import Message
from apps.vacancies.models import Vacancy
from tests.factories import (
    ApplicationFactory,
    CompanyMembershipFactory,
    UserFactory,
    VacancyFactory,
)


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


def test_hr_assistant_vacancy_ambiguity_is_not_reported_as_action_error():
    response = build_hr_response(
        gpt_message="Which Senior React Developer vacancy should I use: published or archived?",
        actions_taken=[
            {
                "tool": "list_candidates",
                "result": {
                    "success": False,
                    "action": "clarify",
                    "message": "Multiple vacancies match.",
                },
            }
        ],
    )

    assert response["success"] is True
    assert response["message"] == "Which Senior React Developer vacancy should I use: published or archived?"


def test_list_candidates_duplicate_vacancy_title_returns_clarification(company, hr_user):
    CompanyMembershipFactory(user=hr_user, company=company, role=hr_user.role)
    published = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Senior React Developer",
        status=Vacancy.Status.PUBLISHED,
    )
    archived = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Senior React Developer",
        status=Vacancy.Status.ARCHIVED,
    )
    ApplicationFactory(vacancy=published)
    ApplicationFactory(vacancy=published)
    ApplicationFactory(vacancy=archived)

    result = execute_tool(
        user=hr_user,
        name="list_candidates",
        args={"vacancy_title": "Senior React Developer"},
    )

    assert result["success"] is False
    assert result["action"] == "clarify"
    assert result["code"] == "ambiguous_vacancy"
    assert "published" in result["message"]
    assert "archived" in result["message"]
    assert "error" not in result
    choices = result["data"]["choices"]
    assert {choice["status"] for choice in choices} == {
        Vacancy.Status.PUBLISHED,
        Vacancy.Status.ARCHIVED,
    }
    assert sorted(choice["candidates_total"] for choice in choices) == [1, 2]


def test_list_candidates_can_disambiguate_duplicate_vacancy_title_by_status(company, hr_user):
    CompanyMembershipFactory(user=hr_user, company=company, role=hr_user.role)
    published = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Senior React Developer",
        status=Vacancy.Status.PUBLISHED,
    )
    VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Senior React Developer",
        status=Vacancy.Status.ARCHIVED,
    )
    ApplicationFactory(vacancy=published, candidate_name="Alex React")

    result = execute_tool(
        user=hr_user,
        name="list_candidates",
        args={
            "vacancy_title": "Senior React Developer",
            "vacancy_status": Vacancy.Status.PUBLISHED,
        },
    )

    assert result["success"] is True
    assert result["action"] == "list_candidates"
    assert result["data"][0]["name"] == "Alex React"


def test_send_candidate_message_tool_uses_central_delivery_service(company, hr_user):
    CompanyMembershipFactory(user=hr_user, company=company, role=hr_user.role)
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE)
    vacancy = VacancyFactory(company=company, created_by=hr_user, title="Backend Engineer")
    application = ApplicationFactory(
        vacancy=vacancy,
        candidate=candidate,
        candidate_name="Alex Candidate",
        candidate_email=candidate.email,
    )

    result = execute_tool(
        user=hr_user,
        name="send_candidate_message",
        args={
            "candidate_email_or_name": candidate.email,
            "vacancy_title": "Backend Engineer",
            "message": "Please review the next step.",
        },
    )

    assert result["success"] is True
    assert result["action"] == "send_candidate_message"
    assert result["data"]["application_id"] == str(application.id)
    assert result["data"]["delivery_channel"] == Message.DeliveryChannel.WEB


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
