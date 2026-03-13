from django.db import models, transaction

from apps.accounts.models import Company, User
from apps.common.exceptions import ApplicationError
from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria


DEFAULT_CRITERIA = [
    {"name": "Technical Skills", "description": "Relevant technical knowledge and abilities", "weight": 3, "order": 0},
    {"name": "Communication", "description": "Clarity of expression and listening skills", "weight": 2, "order": 1},
    {"name": "Problem Solving", "description": "Analytical thinking and creative solutions", "weight": 3, "order": 2},
    {"name": "Cultural Fit", "description": "Alignment with company values and team dynamics", "weight": 2, "order": 3},
    {"name": "Experience Relevance", "description": "Relevance of prior experience to the role", "weight": 2, "order": 4},
]


@transaction.atomic
def create_vacancy(
    *,
    company: Company,
    created_by: User,
    title: str,
    description: str,
    **kwargs: object,
) -> Vacancy:
    """Create a vacancy with default evaluation criteria."""
    vacancy = Vacancy.objects.create(
        company=company,
        created_by=created_by,
        title=title,
        description=description,
        **kwargs,
    )
    create_default_criteria(vacancy=vacancy)
    return vacancy


def update_vacancy(*, vacancy: Vacancy, data: dict) -> Vacancy:
    """Update allowed vacancy fields."""
    allowed_fields = {
        "title", "description", "requirements", "responsibilities",
        "skills", "salary_min", "salary_max", "salary_currency",
        "location", "is_remote", "employment_type", "experience_level",
        "deadline", "visibility", "interview_duration",
    }
    update_fields: list[str] = []

    for field, value in data.items():
        if field in allowed_fields:
            setattr(vacancy, field, value)
            update_fields.append(field)

    if not update_fields:
        return vacancy

    update_fields.append("updated_at")
    vacancy.save(update_fields=update_fields)
    return vacancy


def publish_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Publish a vacancy. It must have at least one question."""
    if vacancy.status == Vacancy.Status.PUBLISHED:
        raise ApplicationError("Vacancy is already published.")

    if vacancy.status == Vacancy.Status.CLOSED:
        raise ApplicationError("Cannot publish a closed vacancy.")

    if not vacancy.questions.filter(is_active=True).exists():
        raise ApplicationError("Cannot publish a vacancy without active questions.")

    vacancy.status = Vacancy.Status.PUBLISHED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def pause_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Pause a published vacancy."""
    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError("Only published vacancies can be paused.")

    vacancy.status = Vacancy.Status.PAUSED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def close_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Close a vacancy."""
    if vacancy.status == Vacancy.Status.CLOSED:
        raise ApplicationError("Vacancy is already closed.")

    vacancy.status = Vacancy.Status.CLOSED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def create_default_criteria(*, vacancy: Vacancy) -> list[VacancyCriteria]:
    """Create the default set of evaluation criteria for a vacancy."""
    criteria_list = []
    for item in DEFAULT_CRITERIA:
        criteria = VacancyCriteria.objects.create(
            vacancy=vacancy,
            name=item["name"],
            description=item["description"],
            weight=item["weight"],
            order=item["order"],
            is_default=True,
        )
        criteria_list.append(criteria)
    return criteria_list


def add_vacancy_criteria(
    *,
    vacancy: Vacancy,
    name: str,
    description: str = "",
    weight: int = 1,
) -> VacancyCriteria:
    """Add a custom evaluation criteria to a vacancy."""
    max_order = vacancy.criteria.aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

    return VacancyCriteria.objects.create(
        vacancy=vacancy,
        name=name,
        description=description,
        weight=weight,
        is_default=False,
        order=max_order + 1,
    )


def update_vacancy_criteria(*, criteria: VacancyCriteria, **kwargs: object) -> VacancyCriteria:
    """Update a vacancy criteria."""
    allowed_fields = {"name", "description", "weight", "order"}
    update_fields: list[str] = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(criteria, field, value)
            update_fields.append(field)

    if not update_fields:
        return criteria

    update_fields.append("updated_at")
    criteria.save(update_fields=update_fields)
    return criteria


def delete_vacancy_criteria(*, criteria: VacancyCriteria) -> None:
    """Delete a vacancy criteria."""
    criteria.delete()


def add_interview_question(
    *,
    vacancy: Vacancy,
    text: str,
    category: str = "",
    source: str = "hr_added",
) -> InterviewQuestion:
    """Add an interview question to a vacancy."""
    max_order = vacancy.questions.aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

    return InterviewQuestion.objects.create(
        vacancy=vacancy,
        text=text,
        category=category,
        source=source,
        order=max_order + 1,
    )


def update_interview_question(*, question: InterviewQuestion, **kwargs: object) -> InterviewQuestion:
    """Update an interview question."""
    allowed_fields = {"text", "category", "order", "is_active"}
    update_fields: list[str] = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(question, field, value)
            update_fields.append(field)

    if not update_fields:
        return question

    update_fields.append("updated_at")
    question.save(update_fields=update_fields)
    return question


def delete_interview_question(*, question: InterviewQuestion) -> None:
    """Delete an interview question."""
    question.delete()


def generate_interview_questions(*, vacancy: Vacancy) -> list[InterviewQuestion]:
    """Generate placeholder interview questions based on vacancy details.

    STUB: Will integrate OpenAI in Phase 7.
    """
    placeholder_questions = [
        {
            "text": f"Tell us about your experience related to {vacancy.title}.",
            "category": "Experience",
        },
        {
            "text": "Describe a challenging project you worked on and how you handled it.",
            "category": "Problem Solving",
        },
        {
            "text": "How do you prioritize tasks when working on multiple projects?",
            "category": "Organization",
        },
        {
            "text": "What motivates you in your professional career?",
            "category": "Behavioral",
        },
        {
            "text": "Where do you see yourself in the next few years?",
            "category": "Career Goals",
        },
    ]

    max_order = vacancy.questions.aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

    created_questions: list[InterviewQuestion] = []
    for i, q in enumerate(placeholder_questions, start=1):
        question = InterviewQuestion.objects.create(
            vacancy=vacancy,
            text=q["text"],
            category=q["category"],
            source=InterviewQuestion.Source.AI_GENERATED,
            order=max_order + i,
        )
        created_questions.append(question)

    return created_questions
