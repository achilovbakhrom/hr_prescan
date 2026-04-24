import json
import logging

from django.conf import settings
from django.db import models
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_AI_QUESTIONS_FAILED
from apps.vacancies.models import InterviewQuestion, ScreeningStep, Vacancy

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {"en": "English", "ru": "Russian", "uz": "Uzbek"}


def _language_instruction(lang_code: str) -> str:
    name = LANGUAGE_NAMES.get(lang_code, "English")
    return f"Write ALL output text (including each question's 'text' field) in {name}. Do not mix languages."


def generate_interview_questions(*, vacancy: Vacancy, step: str = ScreeningStep.PRESCANNING) -> list[InterviewQuestion]:
    """Generate questions using Gemini based on vacancy details and step type."""
    skills_text = ", ".join(vacancy.skills) if vacancy.skills else "not specified"
    criteria = list(vacancy.criteria.filter(step=step).values_list("name", flat=True))
    criteria_text = ", ".join(criteria) if criteria else "general assessment"
    language_instruction = _language_instruction(vacancy.prescanning_language)

    if step == ScreeningStep.PRESCANNING:
        step_instruction = (
            "Generate 4-7 direct candidate-facing questions for a QUICK initial AI prescanning. "
            "Focus on foundational skills, basic fit, motivation, and general "
            "qualifications."
        )
    else:
        step_instruction = (
            "Generate 7-10 direct candidate-facing questions for a RIGOROUS AI interview. "
            "Focus on deeper technical skills, real-world problem solving, "
            "domain expertise, and advanced knowledge."
        )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text=f"Role: {vacancy.title}\n"
                            f"Experience level: {vacancy.experience_level}\n"
                            f"Description: {vacancy.description[:1000]}\n"
                            f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                            f"Skills: {skills_text}\n"
                            f"Evaluation criteria: {criteria_text}"
                        )
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                system_instruction=(
                    f"You are an expert HR interviewer. {step_instruction}\n\n"
                    f"{language_instruction}\n\n"
                    "Each item MUST be a literal question that can be shown directly "
                    "to the candidate in chat. Do NOT write evaluation goals, rubric "
                    'statements, or sentences starting like "Candidate should..." or '
                    '"Кандидат должен...".\n\n'
                    "Good examples:\n"
                    '- "Can you describe a project where you used React hooks to solve a real UI problem?"\n'
                    '- "How do you usually design and validate a REST API before implementation?"\n'
                    '- "Tell me about a time when you had to work under a tight deadline. What did you do?"\n'
                    '- "Какие шаги вы выполняете при проверке пропусков и регистрации номеров транспорта?"\n\n'
                    "Make questions specific to the role, concise, natural, and answerable by a candidate.\n\n"
                    "Return JSON with a 'questions' array. Each item has:\n"
                    '- "text": the literal question to ask the candidate\n'
                    '- "category": one of "Hard Skill", "Soft Skill", "Domain Knowledge", "Cultural Fit"'
                ),
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        data = json.loads(response.text)
        questions_data = data.get("questions", [])
    except Exception as exc:
        logger.exception("Failed to generate questions with AI for vacancy %s", vacancy.id)
        raise ApplicationError(str(MSG_AI_QUESTIONS_FAILED)) from exc

    max_order = vacancy.questions.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    created_questions: list[InterviewQuestion] = []
    for i, q in enumerate(questions_data, start=1):
        question = InterviewQuestion.objects.create(
            vacancy=vacancy,
            text=q.get("text", ""),
            category=q.get("category", "General"),
            source=InterviewQuestion.Source.AI_GENERATED,
            order=max_order + i,
            step=step,
        )
        created_questions.append(question)

    return created_questions


def generate_vacancy_keywords(*, vacancy: Vacancy) -> list[str]:
    """Generate search keywords using AI for a vacancy."""
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=f"Title: {vacancy.title}\n"
                        f"Description: {vacancy.description[:2000]}\n"
                        f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                        f"Skills: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}"
                    )
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "Generate 20-30 search keywords for this job vacancy. "
                "Include ALL of these categories:\n"
                "- Job title synonyms and variations\n"
                "- Broad field/industry terms (e.g. 'programming', 'software development', 'IT')\n"
                "- Related roles and specializations\n"
                "- Key skills and technologies mentioned\n"
                "- Industry jargon and abbreviations\n"
                "- Common search terms a job seeker would use\n"
                "Generate keywords in BOTH English and Russian. "
                'Return JSON: {"keywords": ["keyword1", "keyword2", ...]}'
            ),
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    data = json.loads(response.text)
    keywords = data.get("keywords", [])
    vacancy.keywords = keywords
    vacancy.save(update_fields=["keywords", "updated_at"])
    return keywords


def update_vacancy_search_vector(*, vacancy: Vacancy) -> None:
    """Update the pre-computed search vector for a vacancy.

    Uses both 'english' (for stemming: program matches programming) and
    'simple' (for exact matches of non-English words like Russian).
    """
    from django.contrib.postgres.search import SearchVector
    from django.db.models import Value

    skills_text = " ".join(vacancy.skills) if vacancy.skills else ""
    keywords_text = " ".join(vacancy.keywords) if vacancy.keywords else ""

    Vacancy.objects.filter(id=vacancy.id).update(
        search_vector=(
            # English stemming (program -> programming, develop -> developer)
            SearchVector("title", weight="A", config="english")
            + SearchVector(Value(skills_text), weight="A", config="english")
            + SearchVector(Value(keywords_text), weight="A", config="english")
            + SearchVector("requirements", weight="B", config="english")
            + SearchVector("description", weight="C", config="english")
            # Simple config for exact matches (Russian words, abbreviations)
            + SearchVector("title", weight="A", config="simple")
            + SearchVector(Value(skills_text), weight="A", config="simple")
            + SearchVector(Value(keywords_text), weight="A", config="simple")
        )
    )
