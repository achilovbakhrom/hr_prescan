import pytest

from tests.factories import (
    CompanyFactory,
    UserFactory,
    VacancyFactory,
)
from apps.vacancies.models import InterviewQuestion, ScreeningStep, VacancyCriteria


@pytest.fixture(autouse=True)
def db_access(db):
    """Grant database access to every test automatically."""
    pass


@pytest.fixture()
def company():
    """Create a Company instance."""
    return CompanyFactory()


@pytest.fixture()
def hr_user(company):
    """Create an HR User linked to the company."""
    return UserFactory(company=company, role="hr")


@pytest.fixture()
def candidate_user():
    """Create a Candidate User (no company)."""
    return UserFactory(company=None, role="candidate")


@pytest.fixture()
def vacancy(company, hr_user):
    """Create a published Vacancy with default criteria and a prescanning question."""
    vac = VacancyFactory(
        company=company,
        created_by=hr_user,
        status="published",
    )
    # Create default criteria
    default_criteria = [
        {"name": "Technical Skills", "weight": 3, "order": 0},
        {"name": "Communication", "weight": 2, "order": 1},
        {"name": "Problem Solving", "weight": 3, "order": 2},
        {"name": "Cultural Fit", "weight": 2, "order": 3},
        {"name": "Experience Relevance", "weight": 2, "order": 4},
    ]
    for item in default_criteria:
        VacancyCriteria.objects.create(
            vacancy=vac,
            name=item["name"],
            weight=item["weight"],
            order=item["order"],
            is_default=True,
            step=ScreeningStep.PRESCANNING,
        )
    # Create a prescanning question so the vacancy can be considered valid
    InterviewQuestion.objects.create(
        vacancy=vac,
        text="Tell me about yourself and why you are interested in this role.",
        category="Behavioral",
        source=InterviewQuestion.Source.HR_ADDED,
        order=1,
        step=ScreeningStep.PRESCANNING,
    )
    return vac
