from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview
from apps.vacancies.models import ScreeningStep, Vacancy
from apps.vacancies.serializers import VacancyDetailOutputSerializer
from apps.vacancies.services import (
    archive_vacancy,
    create_default_criteria,
    create_vacancy,
    generate_interview_questions,
    generate_vacancy_content,
    generate_vacancy_criteria,
    pause_vacancy,
    publish_vacancy,
)
from tests.factories import ApplicationFactory, InterviewFactory, VacancyFactory


class TestCreateVacancy:
    def test_create_vacancy_with_default_criteria(self, company, hr_user):
        """Creating a vacancy produces 5 default prescanning criteria."""
        vac = create_vacancy(
            company=company,
            created_by=hr_user,
            title="Backend Developer",
            description="We need a backend developer.",
        )

        criteria = vac.criteria.filter(is_default=True, step=ScreeningStep.PRESCANNING)
        assert criteria.count() == 5

        names = set(criteria.values_list("name", flat=True))
        assert "Technical Skills" in names
        assert "Communication" in names
        assert "Problem Solving" in names
        assert "Cultural Fit" in names
        assert "Experience Relevance" in names
        assert list(criteria.order_by("order").values_list("order", flat=True)) == [1, 2, 3, 4, 5]
        assert isinstance(vac.telegram_code, int)
        assert 100000 <= vac.telegram_code <= 999999
        assert VacancyDetailOutputSerializer(vac).data["telegram_code"] == vac.telegram_code

    def test_vacancy_telegram_code_must_be_six_digits(self, company, hr_user):
        """Telegram vacancy codes are always six-digit numeric codes."""
        vac = Vacancy(
            company=company,
            created_by=hr_user,
            title="Backend Developer",
            description="We need a backend developer.",
            telegram_code=12345,
        )

        with pytest.raises(ValidationError):
            vac.full_clean()


class TestGenerateInterviewQuestions:
    def test_generates_literal_candidate_questions(self, vacancy):
        class FakeResponse:
            text = (
                '{"questions": ['
                '{"text": "Какие шаги вы выполняете при проверке пропусков?", '
                '"category": "Domain Knowledge"}'
                "]}"
            )

        with patch("apps.vacancies.services.vacancy_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.return_value = FakeResponse()

            questions = generate_interview_questions(vacancy=vacancy, step=ScreeningStep.PRESCANNING)

        assert len(questions) == 1
        assert questions[0].text == "Какие шаги вы выполняете при проверке пропусков?"
        assert questions[0].category == "Domain Knowledge"
        _, kwargs = client.models.generate_content.call_args
        instruction = kwargs["config"].system_instruction
        assert "literal question" in instruction
        assert "Candidate should" in instruction
        assert "evidence-based questions" in instruction
        assert "discriminatory" in instruction
        assert "Return JSON with a 'questions' array" in instruction
        assert "Return JSON with a 'competencies' array" not in instruction


class TestGenerateVacancyCriteria:
    def test_generates_role_specific_criteria(self, vacancy):
        class FakeResponse:
            text = (
                '{"criteria": ['
                '{"name": "API Design", '
                '"description": "Can explain pragmatic REST API design tradeoffs", '
                '"weight": 4}'
                "]}"
            )

        with patch("apps.vacancies.services.criteria_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.return_value = FakeResponse()
            initial_max_order = vacancy.criteria.filter(step=ScreeningStep.PRESCANNING).order_by("-order")[0].order

            criteria = generate_vacancy_criteria(vacancy=vacancy, step=ScreeningStep.PRESCANNING)

        assert len(criteria) == 1
        assert criteria[0].name == "API Design"
        assert criteria[0].description == "Can explain pragmatic REST API design tradeoffs"
        assert criteria[0].weight == 4
        assert criteria[0].is_default is False
        assert criteria[0].order == initial_max_order + 1
        _, kwargs = client.models.generate_content.call_args
        instruction = kwargs["config"].system_instruction
        assert "evaluation criterion" in instruction
        assert "not a candidate-facing question" in instruction
        assert "observable from a short AI screening conversation" in instruction
        assert "discriminatory" in instruction


class TestGenerateVacancyContent:
    def test_generates_and_grades_vacancy_content(self):
        class DraftResponse:
            text = (
                '{"description": "<p>Build backend APIs.</p>", '
                '"requirements": "- Python\\n- Django", '
                '"responsibilities": "- Build APIs\\n- Review code"}'
            )

        class GradeResponse:
            text = '{"score": 9, "notes": []}'

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [DraftResponse(), GradeResponse()]

            content = generate_vacancy_content(title="Backend Developer", language="en")

        assert content["description"] == "<p>Build backend APIs.</p>"
        assert content["requirements"] == "- Python\n- Django"
        assert content["responsibilities"] == "- Build APIs\n- Review code"
        assert client.models.generate_content.call_count == 2

        generation_instruction = client.models.generate_content.call_args_list[0].kwargs["config"].system_instruction
        grading_instruction = client.models.generate_content.call_args_list[1].kwargs["config"].system_instruction
        assert "Do not invent company names" in generation_instruction
        assert "discriminatory" in generation_instruction
        assert "strict AI quality reviewer" in grading_instruction
        assert "no invented facts" in grading_instruction

    def test_revises_low_scoring_vacancy_content(self):
        class DraftResponse:
            text = (
                '{"description": "<p>Great opportunity.</p>", '
                '"requirements": "- Hard worker", '
                '"responsibilities": "- Do tasks"}'
            )

        class GradeResponse:
            text = '{"score": 6, "notes": ["too generic"]}'

        class RevisedResponse:
            text = (
                '{"description": "<p>Develop and maintain backend services for product workflows.</p>", '
                '"requirements": "- Python\\n- Django\\n- REST API design", '
                '"responsibilities": "- Build APIs\\n- Improve reliability\\n- Collaborate with frontend"}'
            )

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [
                DraftResponse(),
                GradeResponse(),
                RevisedResponse(),
            ]

            content = generate_vacancy_content(title="Backend Developer", language="en")

        assert "backend services" in content["description"]
        assert client.models.generate_content.call_count == 3
        revision_instruction = client.models.generate_content.call_args_list[2].kwargs["config"].system_instruction
        assert "reviewer notes" in revision_instruction
        assert "Keep only facts supported" in revision_instruction

    def test_accepts_markdown_fenced_json_response(self):
        class DraftResponse:
            text = (
                '```json\n{"description": "<p>Build backend APIs.</p>", '
                '"requirements": "- Python", '
                '"responsibilities": "- Build services"}\n```'
            )

        class GradeResponse:
            text = '```json\n{"score": 9, "notes": []}\n```'

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [DraftResponse(), GradeResponse()]

            content = generate_vacancy_content(title="Backend Developer", language="en")

        assert content["description"] == "<p>Build backend APIs.</p>"
        assert content["requirements"] == "- Python"
        assert content["responsibilities"] == "- Build services"
        assert content["generation_context"]["turns"][-1]["content"]["requirements"] == "- Python"

    def test_revises_empty_draft_even_with_high_grade(self):
        class DraftResponse:
            text = "{}"

        class GradeResponse:
            text = '{"score": 9, "notes": []}'

        class RevisedResponse:
            text = (
                '{"description": "<p>Build backend APIs.</p>", '
                '"requirements": "- Python", '
                '"responsibilities": "- Build services"}'
            )

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [DraftResponse(), GradeResponse(), RevisedResponse()]

            content = generate_vacancy_content(title="Backend Developer", language="en")

        assert content["description"] == "<p>Build backend APIs.</p>"
        assert client.models.generate_content.call_count == 3

    def test_regeneration_uses_current_content_instruction_and_previous_context(self):
        class DraftResponse:
            text = (
                '{"description": "<p>Expanded backend API role.</p>", '
                '"requirements": "- Python\\n- Django", '
                '"responsibilities": "- Build APIs\\n- Review code"}'
            )

        class GradeResponse:
            text = '{"score": 9, "notes": []}'

        previous_context = {
            "turns": [
                {
                    "instruction": "First draft",
                    "content": {
                        "description": "<p>Old draft.</p>",
                        "requirements": "- Python",
                        "responsibilities": "- Build APIs",
                    },
                }
            ]
        }

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [DraftResponse(), GradeResponse()]

            content = generate_vacancy_content(
                title="Backend Developer",
                language="en",
                description="<p>Current description.</p>",
                requirements="- Current requirement",
                responsibilities="- Current responsibility",
                additional_instruction="Extend the description section",
                generation_context=previous_context,
            )

        first_payload = client.models.generate_content.call_args_list[0].kwargs["contents"][0].parts[0].text
        assert "Current description: <p>Current description.</p>" in first_payload
        assert "Additional HR instruction: Extend the description section" in first_payload
        assert "First draft" in first_payload
        assert content["generation_context"]["turns"][0]["instruction"] == "First draft"
        assert content["generation_context"]["turns"][-1]["instruction"] == "Extend the description section"

    def test_rejects_empty_final_content(self):
        class EmptyResponse:
            text = "{}"

        class GradeResponse:
            text = '{"score": 9, "notes": []}'

        with patch("apps.vacancies.services.vacancy_content_ai.genai.Client") as client_cls:
            client = client_cls.return_value
            client.models.generate_content.side_effect = [EmptyResponse(), GradeResponse(), EmptyResponse()]

            with pytest.raises(ApplicationError):
                generate_vacancy_content(title="Backend Developer", language="en")


class TestPublishVacancy:
    def test_publish_does_not_require_prescanning_questions(self, company, hr_user):
        """Questions are optional guidance; criteria are enough to publish."""
        vac = VacancyFactory(
            company=company,
            created_by=hr_user,
            status=Vacancy.Status.DRAFT,
        )
        create_default_criteria(vacancy=vac, step=ScreeningStep.PRESCANNING)

        published = publish_vacancy(vacancy=vac)

        assert published.status == Vacancy.Status.PUBLISHED

    def test_publish_with_interview_requires_interview_criteria(self, company, hr_user):
        """If interview_enabled, publishing requires interview criteria, not questions."""
        vac = VacancyFactory(
            company=company,
            created_by=hr_user,
            status=Vacancy.Status.DRAFT,
            interview_enabled=True,
        )
        create_default_criteria(vacancy=vac, step=ScreeningStep.PRESCANNING)

        with pytest.raises(ApplicationError, match="interview evaluation criteria"):
            publish_vacancy(vacancy=vac)


class TestVacancyLifecycle:
    def test_vacancy_lifecycle_forward_only(self, vacancy):
        """draft -> published -> archived works; archived -> draft fails.

        Note: the fixture provides a published vacancy, so we archive it
        and then verify going back to draft is not allowed.
        """
        # Already published via fixture; archive it
        archived = archive_vacancy(vacancy=vacancy)
        assert archived.status == Vacancy.Status.ARCHIVED

        # Cannot go back to draft
        with pytest.raises(ApplicationError):
            publish_vacancy(vacancy=archived)

    def test_pause_and_resume(self, vacancy):
        """published -> paused -> published works."""
        paused = pause_vacancy(vacancy=vacancy)
        assert paused.status == Vacancy.Status.PAUSED

        resumed = publish_vacancy(vacancy=paused)
        assert resumed.status == Vacancy.Status.PUBLISHED


class TestArchiveVacancy:
    def test_archive_expires_pending_sessions(self, vacancy):
        """Archiving a vacancy expires all pending interview sessions."""
        app = ApplicationFactory(vacancy=vacancy, status="applied")
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.PENDING,
        )

        archive_vacancy(vacancy=vacancy)

        session.refresh_from_db()
        assert session.status == Interview.Status.EXPIRED
