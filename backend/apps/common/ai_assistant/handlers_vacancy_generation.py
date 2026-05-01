"""Handlers for AI-generated vacancy setup operations."""

from apps.common.ai_assistant.resolvers import resolve_vacancy


def handle_generate_questions(*, user, params):
    from apps.vacancies.services import generate_interview_questions

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    step = params.get("step", "prescanning")
    questions = generate_interview_questions(vacancy=vacancy, step=step)
    data = [{"text": q.text, "category": q.category} for q in questions]
    return {
        "success": True,
        "message": f"Generated {len(data)} {step} questions for '{vacancy.title}'.",
        "data": data,
        "action": "generate_questions",
    }


def handle_generate_criteria(*, user, params):
    from apps.vacancies.services import generate_vacancy_criteria

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    step = params.get("step", "prescanning")
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
