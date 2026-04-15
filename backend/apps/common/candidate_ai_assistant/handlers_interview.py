import json
import logging

logger = logging.getLogger(__name__)


def _handle_prepare_for_interview(*, user, params):
    from django.conf import settings

    from google import genai
    from google.genai import types

    vacancy_id = params.get("vacancy_id")
    vacancy_title = params.get("vacancy_title", "")

    # Try to load vacancy details if ID provided
    vacancy_context = ""
    if vacancy_id:
        from apps.vacancies.models import Vacancy

        try:
            vacancy = Vacancy.objects.get(
                id=vacancy_id,
                status=Vacancy.Status.PUBLISHED,
                is_deleted=False,
            )
            vacancy_title = vacancy.title
            vacancy_context = (
                f"Job Title: {vacancy.title}\n"
                f"Description: {vacancy.description[:1500]}\n"
                f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                f"Skills: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}\n"
                f"Experience Level: {vacancy.experience_level}\n"
            )
        except (Vacancy.DoesNotExist, ValueError):
            pass  # Fall through to use vacancy_title

    if not vacancy_title and not vacancy_context:
        return {
            "success": False,
            "message": "Please tell me which job you want to prepare for — provide a job title or ID.",
            "data": {},
            "action": "prepare_for_interview",
        }

    if not vacancy_context:
        vacancy_context = f"Job Title: {vacancy_title}\n"

    prompt = (
        f"Generate interview preparation materials for a candidate applying to this role:\n\n"
        f"{vacancy_context}\n"
        f"Provide:\n"
        f"1. 5-7 likely interview questions (mix of technical and behavioral)\n"
        f"2. For each question, a brief tip on how to answer well\n"
        f"3. 3-4 general interview tips specific to this role\n\n"
        f"Return as a JSON object with this structure:\n"
        f'{{"questions": [{{"question": "...", "tip": "..."}}], "general_tips": ["..."]}}\n'
        f"Return ONLY the JSON, nothing else."
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.4,
            ),
        )
        raw = response.text.strip()
        # Try to parse as JSON
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        prep_data = json.loads(raw)
    except Exception as e:
        logger.error("Interview prep error: %s", e)
        return {
            "success": False,
            "message": "Failed to generate interview preparation materials. Please try again.",
            "data": {},
            "action": "prepare_for_interview",
        }

    return {
        "success": True,
        "message": f"Here's your interview preparation for '{vacancy_title}':",
        "data": prep_data,
        "action": "prepare_for_interview",
    }
