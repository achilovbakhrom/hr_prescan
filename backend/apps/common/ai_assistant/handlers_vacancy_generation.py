"""Handlers for AI-generated vacancy setup operations."""

from apps.common.ai_assistant.resolvers import resolve_vacancy
from apps.vacancies.models import ScreeningStep


def ensure_vacancy_screening_setup(*, vacancy, step: str) -> tuple[list, list]:
    """Create missing criteria/questions needed before publishing a vacancy."""
    from apps.vacancies.services import generate_interview_questions, generate_vacancy_criteria

    generated_criteria = []
    if not vacancy.criteria.filter(step=step).exists():
        generated_criteria = generate_vacancy_criteria(vacancy=vacancy, step=step)

    generated_questions = []
    if not vacancy.questions.filter(is_active=True, step=step).exists():
        generated_questions = generate_interview_questions(vacancy=vacancy, step=step)

    return generated_criteria, generated_questions


def handle_generate_questions(*, user, params):
    from apps.vacancies.services import generate_interview_questions

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    step = params.get("step", ScreeningStep.PRESCANNING)
    criteria = []
    if not vacancy.criteria.filter(step=step).exists():
        from apps.vacancies.services import generate_vacancy_criteria

        criteria = generate_vacancy_criteria(vacancy=vacancy, step=step)
    questions = generate_interview_questions(vacancy=vacancy, step=step)
    data = {
        "criteria": [{"name": c.name, "description": c.description, "weight": c.weight} for c in criteria],
        "questions": [{"text": q.text, "category": q.category} for q in questions],
    }
    criteria_note = f" and {len(criteria)} criteria" if criteria else ""
    return {
        "success": True,
        "message": f"Generated {len(data['questions'])} {step} questions{criteria_note} for '{vacancy.title}'.",
        "data": data,
        "action": "generate_questions",
    }


def handle_generate_criteria(*, user, params):
    from apps.vacancies.services import generate_vacancy_criteria

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    step = params.get("step", ScreeningStep.PRESCANNING)
    criteria = generate_vacancy_criteria(vacancy=vacancy, step=step)
    data = [{"name": c.name, "description": c.description, "weight": c.weight} for c in criteria]
    return {
        "success": True,
        "message": f"Generated {len(data)} {step} criteria for '{vacancy.title}'.",
        "data": data,
        "action": "generate_criteria",
    }


def handle_regenerate_keywords(*, user, params):
    from apps.vacancies.services import generate_vacancy_keywords

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    keywords = generate_vacancy_keywords(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Regenerated {len(keywords)} keywords for '{vacancy.title}'.",
        "data": {"keywords": keywords},
        "action": "regenerate_keywords",
    }
