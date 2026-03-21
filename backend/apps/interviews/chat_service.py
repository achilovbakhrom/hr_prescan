"""
AI chat interview service — handles conversation with candidates via OpenAI.

Responsibilities:
- Build system prompt from vacancy + CV + questions
- Generate AI greeting
- Process candidate messages and generate AI responses
- Detect when the interview should end
- Trigger scoring/evaluation on completion
"""

import logging

from django.conf import settings
from django.utils import timezone

from openai import OpenAI

from apps.interviews.models import Interview

logger = logging.getLogger(__name__)

INTERVIEW_COMPLETE_MARKER = "[INTERVIEW_COMPLETE]"


def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _build_system_prompt(interview: Interview) -> str:
    """Build the system prompt for the AI interviewer."""
    application = interview.application
    vacancy = application.vacancy

    # Gather interview questions
    questions = list(
        vacancy.questions.filter(is_active=True).order_by("order").values_list("text", flat=True)
    )
    questions_text = "\n".join(f"- {q}" for q in questions) if questions else "No specific questions defined."

    # Gather evaluation criteria
    criteria = list(
        vacancy.criteria.all().order_by("order").values_list("name", "description", "weight")
    )
    criteria_text = "\n".join(
        f"- {name} (weight: {weight}): {desc}" for name, desc, weight in criteria
    ) if criteria else "No specific criteria defined."

    # CV data
    cv_section = ""
    if application.cv_parsed_data:
        cv_data = application.cv_parsed_data
        cv_section = f"""
## Candidate's CV Summary
- Skills: {', '.join(cv_data.get('skills', [])) or 'Not available'}
- Experience: {cv_data.get('experience_years', 'Unknown')} years
- Education: {cv_data.get('education', 'Not available')}
- Languages: {', '.join(cv_data.get('languages', [])) or 'Not available'}
- Summary: {cv_data.get('summary', 'Not available')}

Use this CV data to ask targeted follow-up questions and verify claims.
"""
    elif application.cv_parsed_text:
        cv_section = f"""
## Candidate's CV (raw text)
{application.cv_parsed_text[:2000]}

Use this CV data to ask targeted follow-up questions and verify claims.
"""

    # Company info section
    company_info_section = ""
    company_info = getattr(vacancy, "company_info", "") or ""
    if company_info:
        company_info_section = f"""
## About the Company
{company_info}

Include a brief company introduction in your greeting (1-2 sentences based on the above).
"""

    return f"""You are an AI interviewer conducting a text-based pre-screening interview for the position of "{vacancy.title}" at {vacancy.company.name}.

## Your Role
- Professional, warm, and concise interviewer
- Ask ONE question at a time, wait for response
- Keep your messages SHORT (2-4 sentences max). Candidates prefer brief, clear communication
- Prefix each question with "Q:" to clearly mark it
- Ask follow-up questions when answers are vague or interesting
- Be conversational but professional — this is a chat, not a formal exam
{company_info_section}
## Vacancy Details
- Title: {vacancy.title}
- Description: {vacancy.description[:500]}
- Requirements: {(vacancy.requirements or 'Not specified')[:500]}
- Skills needed: {', '.join(vacancy.skills) if vacancy.skills else 'Not specified'}
- Experience level: {vacancy.get_experience_level_display()}
{cv_section}
## Prepared Interview Questions
{questions_text}

## Evaluation Criteria
{criteria_text}

## Interview Rules
1. Greet the candidate briefly{' and introduce the company' if company_info else ''}, then ask them to introduce themselves
2. Work through the prepared questions, adapting based on answers
3. Ask follow-up questions to probe deeper when needed
4. Keep your responses concise — no long paragraphs or lectures
5. Cover all evaluation criteria through your questions
6. Typically ask 6-10 questions total (including follow-ups)

## IMPORTANT — Early Termination for Unsuitable Candidates
If after 3-4 questions it becomes clear the candidate is significantly underqualified for this role (e.g., an intern applying for a senior position, completely wrong tech stack, no relevant experience at all):
- Politely acknowledge their background
- Kindly explain that this specific role requires a different experience level or skill set
- Thank them for their time and wish them well in their career
- End the interview early with the {INTERVIEW_COMPLETE_MARKER} marker
- Do NOT be harsh — be encouraging and suggest they might be a better fit for other positions

## CRITICAL — Ending the Interview
When you have enough information OR the candidate is clearly unsuitable:
- Send a brief thank-you message
- Append the exact marker {INTERVIEW_COMPLETE_MARKER} at the very end of your final message
- This marker signals the system to end the interview — the candidate will NOT see it
- The marker must be the last thing in your message

## Language
Respond in the same language the candidate uses. If they write in Russian, respond in Russian. If in English, respond in English.

## Style
- Keep messages under 100 words
- Be human and warm, not robotic
- Use simple, clear language
- Don't repeat information the candidate already knows
"""


def generate_greeting(interview: Interview) -> str:
    """Generate the AI's opening message for a chat interview."""
    client = _get_client()
    system_prompt = _build_system_prompt(interview)

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "[SYSTEM: The candidate has just opened the chat. Send a brief, warm greeting (2-3 sentences). Introduce yourself and the company briefly if company info is available. Then ask the candidate to tell you about themselves.]"},
        ],
        max_tokens=300,
        temperature=0.7,
    )

    greeting = response.choices[0].message.content or ""
    # Remove the completion marker from greeting (shouldn't be there, but safety check)
    greeting = greeting.replace(INTERVIEW_COMPLETE_MARKER, "").strip()
    return greeting


def process_candidate_message(interview: Interview, candidate_message: str) -> dict:
    """
    Process a candidate's message and generate the AI response.

    Returns dict with:
    - ai_message: str — the AI's response text (cleaned, no markers)
    - is_complete: bool — whether the interview is now complete
    - chat_history: list — updated chat history
    """
    client = _get_client()
    system_prompt = _build_system_prompt(interview)
    now = timezone.now().isoformat()

    # Build conversation history for OpenAI
    chat_history = list(interview.chat_history or [])

    # Append the new candidate message
    chat_history.append({
        "role": "candidate",
        "text": candidate_message,
        "timestamp": now,
    })

    # Convert our chat history to OpenAI message format
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        role = "assistant" if msg["role"] == "ai" else "user"
        openai_messages.append({"role": role, "content": msg["text"]})

    # Call OpenAI
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=openai_messages,
        max_tokens=400,
        temperature=0.7,
    )

    raw_ai_text = response.choices[0].message.content or ""

    # Check if interview is complete
    is_complete = INTERVIEW_COMPLETE_MARKER in raw_ai_text

    # Clean the marker from the displayed text
    clean_ai_text = raw_ai_text.replace(INTERVIEW_COMPLETE_MARKER, "").strip()

    ai_timestamp = timezone.now().isoformat()

    # Append AI response to history
    chat_history.append({
        "role": "ai",
        "text": clean_ai_text,
        "timestamp": ai_timestamp,
    })

    # Save updated history
    interview.chat_history = chat_history
    update_fields = ["chat_history", "updated_at"]

    if is_complete:
        interview.status = Interview.Status.COMPLETED
        update_fields.append("status")

    interview.save(update_fields=update_fields)

    # If complete, update application status and run evaluation
    if is_complete:
        application = interview.application
        from apps.applications.models import Application
        application.status = Application.Status.INTERVIEW_COMPLETED
        application.save(update_fields=["status", "updated_at"])
        logger.info("Chat interview %s completed, running evaluation...", interview.id)

        try:
            evaluate_chat_interview(interview)
        except Exception as e:
            logger.error("Failed to evaluate interview %s: %s", interview.id, e)

    return {
        "ai_message": clean_ai_text,
        "ai_timestamp": ai_timestamp,
        "is_complete": is_complete,
        "chat_history": chat_history,
    }


def evaluate_chat_interview(interview: Interview) -> None:
    """
    Evaluate a completed chat interview using GPT.

    Analyzes the full transcript and scores the candidate on each
    vacancy criteria. Saves scores, overall score, and AI summary.
    """
    import json
    from apps.interviews.models import InterviewScore

    client = _get_client()
    application = interview.application
    vacancy = application.vacancy

    # Build transcript text
    transcript_lines = []
    for msg in interview.chat_history or []:
        role_label = "Interviewer" if msg["role"] == "ai" else "Candidate"
        transcript_lines.append(f"{role_label}: {msg['text']}")
    transcript_text = "\n\n".join(transcript_lines)

    # Get criteria
    criteria_list = list(
        vacancy.criteria.all().order_by("order").values("id", "name", "description", "weight")
    )

    if not criteria_list:
        logger.warning("No criteria for vacancy %s, skipping evaluation", vacancy.id)
        return

    criteria_json = json.dumps([
        {"id": str(c["id"]), "name": c["name"], "description": c["description"], "weight": c["weight"]}
        for c in criteria_list
    ])

    eval_prompt = f"""You are an expert HR evaluator. Analyze this interview transcript and score the candidate.

## Position
{vacancy.title} at {vacancy.company.name}

## Job Description
{vacancy.description}

## Requirements
{vacancy.requirements or 'Not specified'}

## Evaluation Criteria
{criteria_json}

## Interview Transcript
{transcript_text}

## Your Task
Score the candidate on EACH criteria (1-10 scale) and provide a brief note explaining each score.
Also provide an overall summary (2-3 sentences) and an overall weighted score (1-10).

Respond with ONLY valid JSON in this exact format:
{{
  "scores": [
    {{"criteria_id": "<uuid>", "score": 8, "notes": "Brief explanation"}},
    ...
  ],
  "overall_score": 7.5,
  "summary": "Overall assessment of the candidate in 2-3 sentences."
}}"""

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert HR evaluator. Respond only with valid JSON."},
            {"role": "user", "content": eval_prompt},
        ],
        max_tokens=1500,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Failed to parse evaluation JSON for interview %s", interview.id)
        return

    # Save scores
    valid_criteria_ids = {str(c["id"]) for c in criteria_list}
    score_objects = []
    for score_data in result.get("scores", []):
        cid = score_data.get("criteria_id")
        if cid not in valid_criteria_ids:
            continue
        score_val = max(1, min(10, int(score_data.get("score", 5))))
        score_objects.append(
            InterviewScore(
                interview=interview,
                criteria_id=cid,
                score=score_val,
                ai_notes=score_data.get("notes", ""),
            )
        )

    if score_objects:
        InterviewScore.objects.filter(interview=interview).delete()
        InterviewScore.objects.bulk_create(score_objects)

    # Save overall score and summary
    overall = result.get("overall_score")
    if overall is not None:
        interview.overall_score = min(10, max(0, float(overall)))
    interview.ai_summary = result.get("summary", "")
    interview.transcript = interview.chat_history  # Store chat as transcript too
    interview.save(update_fields=["overall_score", "ai_summary", "transcript", "updated_at"])

    logger.info(
        "Evaluation complete for interview %s: score=%.1f, %d criteria scored",
        interview.id, interview.overall_score or 0, len(score_objects),
    )
