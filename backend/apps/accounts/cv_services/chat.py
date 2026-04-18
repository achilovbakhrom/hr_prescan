import json

from django.conf import settings

from apps.accounts.cv_services.profile import (
    _populate_profile_from_parsed,
    get_or_create_candidate_profile,
)

_CV_CHAT_SYSTEM = """You are an AI career assistant helping a user build their professional CV through a friendly conversation.

YOUR TASK:
Ask questions ONE AT A TIME to collect information for a complete CV. Be concise and conversational.

REQUIRED information to collect (ask about each):
1. Desired job title / position
2. Work experience (companies, roles, dates, achievements)
3. Education (university, degree, field, dates)
4. Key skills
5. Languages spoken and proficiency levels
6. Location (city/country)
7. Desired salary range (min and max) and currency -- or if the user says it's negotiable, accept that
8. Preferred work type (full-time, part-time, contract, or internship)

RULES:
- Ask ONE question at a time. Keep questions short and friendly.
- Respond in the SAME language the user writes in (Russian -> Russian, English -> English).
- After the user answers, acknowledge briefly and move to the next topic.
- If the user gives a short answer, that's fine -- don't push for more detail.
- For salary: accept a range like "2000-3000 USD", a single number, or "negotiable" / "договорная".
- For work type: accept synonyms (full time / полная / полный рабочий день -> full_time; part time / частичная / неполный -> part_time; contract / контракт -> contract; internship / стажировка -> internship).
- Do NOT use markdown formatting.
- When you have collected enough information about ALL required topics, respond with EXACTLY this format:
  [READY]
  Your message to the user confirming you have everything.
- Start by greeting the user and asking about their desired position."""


def cv_chat_next_message(*, messages):
    """Process conversation and return AI's next message.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
    Returns:
        {"status": "continue"|"ready", "message": "AI response text"}
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    contents = [types.Content(role="user", parts=[types.Part(text=_CV_CHAT_SYSTEM)])]
    contents.append(
        types.Content(
            role="model",
            parts=[types.Part(text="Understood. I'll guide the user through building their CV.")],
        )
    )

    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
    )

    text = response.text.strip()

    if "[READY]" in text:
        message = text.split("[READY]", 1)[1].strip()
        return {"status": "ready", "message": message or text.split("[READY]", 1)[0].strip()}

    return {"status": "continue", "message": text}


def cv_chat_generate(*, user, messages):
    """Generate CV from the full conversation history.

    Args:
        user: The authenticated user.
        messages: Full conversation history list.
    Returns:
        The updated CandidateProfile instance.
    """
    from google import genai

    profile = get_or_create_candidate_profile(user=user)
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    conversation_text = "\n".join(f"{'AI' if m['role'] == 'assistant' else 'User'}: {m['content']}" for m in messages)

    prompt = f"""Based on this conversation between an AI career assistant and a user, extract all CV information and generate a complete professional CV.

--- CONVERSATION ---
{conversation_text}

--- INSTRUCTIONS ---
Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "headline": "professional title/headline",
  "summary": "2-3 sentence professional summary",
  "location": "city/country",
  "desired_salary_min": null or number,
  "desired_salary_max": null or number,
  "desired_salary_currency": "USD|EUR|GBP|RUB",
  "desired_salary_negotiable": true/false,
  "desired_employment_type": "full_time|part_time|contract|internship or empty string",
  "work_experiences": [
    {{"company_name": "", "position": "", "employment_type": "full_time|part_time|contract|internship", "location": "", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD or null", "is_current": true/false, "description": "achievements with action verbs"}}
  ],
  "educations": [
    {{"institution": "", "degree": "", "field_of_study": "", "start_date": "YYYY-MM-DD or null", "end_date": "YYYY-MM-DD or null", "description": ""}}
  ],
  "skills": ["skill1", "skill2"],
  "languages": [
    {{"language": "English", "proficiency": "native|advanced|upper_intermediate|intermediate|elementary|beginner"}}
  ],
  "certifications": []
}}

RULES:
- Keep the same language as the user used in conversation.
- Expand brief descriptions into professional bullet points with action verbs.
- List 5-15 relevant skills based on the role and experience.
- Estimate reasonable dates if not explicitly provided.
- Do NOT invent company names or institutions -- only use what the user mentioned.
- If the user only gave a single salary number, set it as both min and max.
- If the user said "negotiable" / "договорная", set desired_salary_negotiable=true and leave min/max null.
- If currency was not mentioned, default to USD.
- Normalize work type synonyms (full time -> full_time, part time -> part_time, стажировка -> internship, контракт -> contract)."""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[prompt],
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    parsed = json.loads(text)

    from django.db import transaction

    from apps.accounts.models import (
        CandidateLanguage,
        Certification,
        Education,
        WorkExperience,
    )

    with transaction.atomic():
        WorkExperience.objects.filter(profile=profile).delete()
        Education.objects.filter(profile=profile).delete()
        CandidateLanguage.objects.filter(profile=profile).delete()
        Certification.objects.filter(profile=profile).delete()
        profile.skills.clear()
        _populate_profile_from_parsed(profile=profile, data=parsed)

    return profile


def improve_cv_section(*, section, content, job_title=None):
    """Use AI to improve a CV section text."""
    from google import genai

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    context = f" tailored for a {job_title} position" if job_title else ""
    prompt = f"""Improve this {section} text for a professional CV{context}.
Make it more impactful, concise, and professional. Use action verbs and quantify achievements where possible.
Keep the same language (if Russian, write in Russian; if English, write in English).
Return ONLY the improved text, no explanations.

Original text:
{content}"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[prompt],
    )

    return response.text.strip()
