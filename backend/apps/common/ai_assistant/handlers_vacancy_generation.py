"""Handlers for AI-generated vacancy setup operations."""

from apps.common.ai_assistant.resolvers import resolve_vacancy
from apps.vacancies.models import ScreeningStep


def ensure_vacancy_screening_setup(*, vacancy, step: str) -> tuple[list, list]:
    """Create missing criteria and draft AI instructions needed before publishing."""
    from apps.vacancies.services import generate_screening_instruction, generate_vacancy_criteria

    generated_criteria = []
    if not vacancy.criteria.filter(step=step).exists():
        generated_criteria = generate_vacancy_criteria(vacancy=vacancy, step=step)

    generated_instructions = []
    prompt_field = "prescanning_prompt" if step == ScreeningStep.PRESCANNING else "interview_prompt"
    if not (getattr(vacancy, prompt_field) or "").strip():
        instruction = generate_screening_instruction(vacancy=vacancy, step=step)
        setattr(vacancy, prompt_field, instruction)
        vacancy.save(update_fields=[prompt_field, "updated_at"])
        generated_instructions.append(instruction)

    return generated_criteria, generated_instructions


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


def handle_generate_instructions(*, user, params):
    from apps.vacancies.services import generate_screening_instruction, update_vacancy

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))
    step = params.get("step", ScreeningStep.PRESCANNING)
    style = params.get("style", "balanced")
    instruction = generate_screening_instruction(vacancy=vacancy, step=step, style=style)
    field = "prescanning_prompt" if step == ScreeningStep.PRESCANNING else "interview_prompt"
    update_vacancy(vacancy=vacancy, data={field: instruction})
    return {
        "success": True,
        "message": f"Generated {step} AI instructions for '{vacancy.title}'.",
        "data": {"instruction": instruction, "step": step, "style": style},
        "action": "generate_instructions",
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
