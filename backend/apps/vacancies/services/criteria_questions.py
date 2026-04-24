from django.db import models

from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_CANNOT_DELETE_LAST_CRITERIA
from apps.vacancies.models import InterviewQuestion, ScreeningStep, Vacancy, VacancyCriteria

DEFAULT_CRITERIA = [
    {
        "name": "Technical Skills",
        "description": "Relevant technical knowledge and abilities",
        "weight": 3,
        "order": 1,
        "translations": {
            "en": "Technical Skills: Relevant technical knowledge and abilities",
            "ru": "Технические навыки: Соответствующие технические знания и навыки",
            "uz": "Texnik ko'nikmalar: Tegishli texnik bilim va ko'nikmalar",
        },
    },
    {
        "name": "Communication",
        "description": "Clarity of expression and listening skills",
        "weight": 2,
        "order": 2,
        "translations": {
            "en": "Communication: Clarity of expression and listening skills",
            "ru": "Коммуникация: Ясность изложения и навыки слушания",
            "uz": "Kommunikatsiya: Fikrni aniq ifodalash va tinglash ko'nikmalari",
        },
    },
    {
        "name": "Problem Solving",
        "description": "Analytical thinking and creative solutions",
        "weight": 3,
        "order": 3,
        "translations": {
            "en": "Problem Solving: Analytical thinking and creative solutions",
            "ru": "Решение проблем: Аналитическое мышление и креативные решения",
            "uz": "Muammolarni hal qilish: Analitik fikrlash va ijodiy yechimlar",
        },
    },
    {
        "name": "Cultural Fit",
        "description": "Alignment with company values and team dynamics",
        "weight": 2,
        "order": 4,
        "translations": {
            "en": "Cultural Fit: Alignment with company values and team dynamics",
            "ru": "Соответствие культуре: Соответствие ценностям компании и динамике команды",
            "uz": "Madaniyatga moslik: Kompaniya qadriyatlari va jamoa dinamikasiga moslik",
        },
    },
    {
        "name": "Experience Relevance",
        "description": "Relevance of prior experience to the role",
        "weight": 2,
        "order": 5,
        "translations": {
            "en": "Experience Relevance: Relevance of prior experience to the role",
            "ru": "Релевантность опыта: Релевантность предыдущего опыта данной роли",
            "uz": "Tajribaning mosligi: Oldingi tajribaning ushbu rolga mosligi",
        },
    },
]


def create_default_criteria(
    *,
    vacancy: Vacancy,
    step: str = ScreeningStep.PRESCANNING,
) -> list[VacancyCriteria]:
    """Create the default set of evaluation criteria for the given step."""
    criteria_list = []
    for item in DEFAULT_CRITERIA:
        criteria = VacancyCriteria.objects.create(
            vacancy=vacancy,
            name=item["name"],
            description=item["description"],
            weight=item["weight"],
            order=item["order"],
            is_default=True,
            step=step,
            translations=item["translations"],
        )
        criteria_list.append(criteria)
    return criteria_list


def add_vacancy_criteria(
    *,
    vacancy: Vacancy,
    name: str,
    description: str = "",
    weight: int = 1,
    step: str = ScreeningStep.PRESCANNING,
) -> VacancyCriteria:
    """Add a custom evaluation criteria to a vacancy."""
    max_order = vacancy.criteria.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    return VacancyCriteria.objects.create(
        vacancy=vacancy,
        name=name,
        description=description,
        weight=weight,
        is_default=False,
        order=max_order + 1,
        step=step,
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
    """Delete a vacancy criteria.

    Refuses to delete the last remaining criteria for a step — without at
    least one criteria, AI scoring at evaluation time would silently produce
    a 0 score.
    """
    siblings = VacancyCriteria.objects.filter(
        vacancy_id=criteria.vacancy_id,
        step=criteria.step,
    ).exclude(id=criteria.id)
    if not siblings.exists():
        raise ApplicationError(str(MSG_CANNOT_DELETE_LAST_CRITERIA))
    criteria.delete()


def add_interview_question(
    *,
    vacancy: Vacancy,
    text: str,
    category: str = "",
    source: str = "hr_added",
    step: str = ScreeningStep.PRESCANNING,
) -> InterviewQuestion:
    """Add a question to a vacancy for the specified step."""
    max_order = vacancy.questions.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    return InterviewQuestion.objects.create(
        vacancy=vacancy,
        text=text,
        category=category,
        source=source,
        order=max_order + 1,
        step=step,
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
