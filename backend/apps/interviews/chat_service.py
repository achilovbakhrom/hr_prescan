"""
AI chat screening service — handles conversation with candidates via OpenAI.

Supports two session types:
- Prescanning: lighter, quicker initial screening (always chat mode)
- Interview: tougher, domain-specific evaluation (chat or meet mode)

Responsibilities:
- Build system prompt from vacancy + CV + questions (filtered by step)
- Generate AI greeting
- Process candidate messages and generate AI responses
- Detect when the session should end and AI decision (advance/reject)
- Trigger scoring/evaluation on completion
"""

import logging

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

from apps.common.messages import MSG_EVALUATION_MALFORMED
from apps.interviews.models import Interview

logger = logging.getLogger(__name__)

SESSION_COMPLETE_ADVANCE = "[SESSION_ADVANCE]"
SESSION_COMPLETE_REJECT = "[SESSION_REJECT]"


def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _build_system_prompt(interview: Interview) -> str:
    """Build the system prompt for the AI agent, differentiated by session type."""
    application = interview.application
    vacancy = application.vacancy
    step = interview.session_type  # "prescanning" or "interview"

    # Filter questions and criteria by step
    questions = list(
        vacancy.questions.filter(is_active=True, step=step).order_by("order").values_list("text", flat=True)
    )
    questions_text = "\n".join(f"- {q}" for q in questions) if questions else "No specific questions defined."

    criteria = list(vacancy.criteria.filter(step=step).order_by("order").values_list("name", "description", "weight"))
    criteria_text = (
        "\n".join(f"- {name} (weight: {weight}): {desc}" for name, desc, weight in criteria)
        if criteria
        else "No specific criteria defined."
    )

    # CV data
    cv_section = ""
    if application.cv_parsed_data:
        cv_data = application.cv_parsed_data
        cv_section = f"""
## Candidate's CV Summary
- Skills: {", ".join(cv_data.get("skills", [])) or "Not available"}
- Experience: {cv_data.get("experience_years", "Unknown")} years
- Education: {cv_data.get("education", "Not available")}
- Languages: {", ".join(cv_data.get("languages", [])) or "Not available"}
- Summary: {cv_data.get("summary", "Not available")}

Use this CV data to ask targeted follow-up questions and verify claims.
"""
    elif application.cv_parsed_text:
        cv_section = f"""
## Candidate's CV (raw text)
{application.cv_parsed_text[:2000]}

Use this CV data to ask targeted follow-up questions and verify claims.
"""

    # Company info section — prefer employer description, fall back to vacancy.company_info
    company_info_section = ""
    company_info = ""
    if vacancy.employer and vacancy.employer.description:
        company_info = vacancy.employer.description
    elif vacancy.company_info:
        company_info = vacancy.company_info
    if company_info:
        company_info_section = f"""
## About the Company
{company_info}

Include a brief company introduction in your greeting (1-2 sentences based on the above).
"""

    # Step-specific additional prompt from HR
    additional_prompt = ""
    if step == Interview.SessionType.PRESCANNING and vacancy.prescanning_prompt:
        additional_prompt = f"""
## Additional Instructions from HR
{vacancy.prescanning_prompt}
"""
    elif step == Interview.SessionType.INTERVIEW and vacancy.interview_prompt:
        additional_prompt = f"""
## Additional Instructions from HR
{vacancy.interview_prompt}
"""

    # Step-specific behavior
    if step == Interview.SessionType.PRESCANNING:
        behavior = _prescanning_behavior(vacancy, company_info)
    else:
        behavior = _interview_behavior(vacancy, company_info)

    return f"""{behavior}
{company_info_section}
## Vacancy Details
- Title: {vacancy.title}
- Description: {vacancy.description[:500]}
- Requirements: {(vacancy.requirements or "Not specified")[:500]}
- Skills needed: {", ".join(vacancy.skills) if vacancy.skills else "Not specified"}
- Experience level: {vacancy.get_experience_level_display()}
{cv_section}{additional_prompt}
## Prepared Questions
{questions_text}

## Evaluation Criteria
{criteria_text}

## CRITICAL — Ending the Session and Making a Decision
When you have enough information to make a decision:
- Send a brief thank-you message to the candidate
- If the candidate should ADVANCE to the next stage, append {SESSION_COMPLETE_ADVANCE} at the very end
- If the candidate should be REJECTED, append {SESSION_COMPLETE_REJECT} at the very end
- These markers signal the system — the candidate will NOT see them
- The marker must be the last thing in your message

## Language
Respond in the same language the candidate uses. If they write in Russian, respond in Russian.
If in English, respond in English.

## Style
- Keep messages under 100 words
- Be human and warm, not robotic
- Use simple, clear language
- Don't repeat information the candidate already knows
"""


def _prescanning_behavior(vacancy, company_info: str) -> str:
    """Build the prescanning-specific behavior prompt."""
    return f"""You are an AI pre-screener conducting a quick text-based prescanning \
for the position of "{vacancy.title}" at {vacancy.company.name}.

## Your Role — Prescanning
- Professional, warm, and concise screener
- This is a QUICK initial screening — keep it light and efficient
- Ask ONE question at a time, wait for response
- Keep your messages SHORT (2-3 sentences max)
- Focus on basic fit: motivation, availability, general qualifications
- Be conversational and friendly — this is the candidate's first impression
- Typically ask 4-6 questions total

## Prescanning Rules
1. Greet the candidate briefly{" and introduce the company" if company_info else ""}, \
then ask them to introduce themselves
2. Work through the prepared questions, adapting based on answers
3. Quickly assess basic fit — don't probe deeply (that's for the interview step)
4. Cover the evaluation criteria through your questions
5. If clearly unqualified after 2-3 questions, wrap up politely

## Decision Criteria
- ADVANCE: Candidate shows basic fit, motivation, and relevant background
- REJECT: Candidate is clearly unqualified, wrong field, or shows red flags"""


def _interview_behavior(vacancy, company_info: str) -> str:
    """Build the interview-specific behavior prompt."""
    return f"""You are an AI interviewer conducting a rigorous text-based interview \
for the position of "{vacancy.title}" at {vacancy.company.name}.

## Your Role — Interview
- Professional and thorough interviewer
- This is a DEEPER evaluation — be more demanding and probing
- Ask ONE question at a time, wait for response
- Keep your messages concise but substantive (2-4 sentences)
- Prefix each question with "Q:" to clearly mark it
- Ask follow-up questions to probe depth of knowledge
- Challenge vague answers — ask for specifics, examples, numbers
- Present practical scenarios or cases when appropriate
- Typically ask 6-10 questions total (including follow-ups)

## Interview Rules
1. Greet the candidate briefly and explain this is the interview stage
2. Work through the prepared questions with rigor
3. Probe deeper — ask for concrete examples, technical details, real-world scenarios
4. Cover all evaluation criteria thoroughly
5. Test claims from their CV or prescanning answers
6. If clearly unqualified, wrap up politely after 4-5 questions

## Decision Criteria
- ADVANCE: Candidate demonstrates strong skills, clear thinking, and domain expertise
- REJECT: Candidate lacks required depth, cannot substantiate claims, or shows significant gaps"""


def generate_greeting(interview: Interview) -> str:
    """Generate the AI's opening message for a chat session."""
    client = _get_client()
    system_prompt = _build_system_prompt(interview)

    step_label = "prescanning" if interview.session_type == Interview.SessionType.PRESCANNING else "interview"

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"[SYSTEM: The candidate has just opened the {step_label} chat. "
                    "Send a brief, warm greeting (2-3 sentences). Introduce yourself and the "
                    "company briefly if company info is available. Then ask the candidate to "
                    "tell you about themselves.]"
                ),
            },
        ],
        max_tokens=300,
        temperature=0.7,
    )

    greeting = response.choices[0].message.content or ""
    # Remove completion markers from greeting (safety check)
    greeting = greeting.replace(SESSION_COMPLETE_ADVANCE, "").replace(SESSION_COMPLETE_REJECT, "").strip()
    return greeting


def _get_ai_response_and_update_history(interview: Interview, candidate_entry: dict) -> dict:
    """
    Shared helper: append candidate entry to history, call OpenAI, handle
    completion markers, save, and run evaluation if complete.

    Args:
        interview: The Interview instance (will be mutated and saved).
        candidate_entry: A dict with at least {role, text, timestamp} and
            optionally {message_type, audio_url, duration}.

    Returns dict with:
        - ai_message: str — the AI's response text (cleaned, no markers)
        - ai_timestamp: str
        - is_complete: bool
        - ai_decision: str | None — "advance" or "reject" if complete
        - chat_history: list — updated chat history
    """
    client = _get_client()
    system_prompt = _build_system_prompt(interview)

    # Build conversation history for OpenAI
    chat_history = list(interview.chat_history or [])
    chat_history.append(candidate_entry)

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

    # Check if session is complete and determine AI decision
    is_complete = SESSION_COMPLETE_ADVANCE in raw_ai_text or SESSION_COMPLETE_REJECT in raw_ai_text
    ai_decision = None
    if SESSION_COMPLETE_ADVANCE in raw_ai_text:
        ai_decision = "advance"
    elif SESSION_COMPLETE_REJECT in raw_ai_text:
        ai_decision = "reject"

    # Clean markers from the displayed text
    clean_ai_text = raw_ai_text.replace(SESSION_COMPLETE_ADVANCE, "").replace(SESSION_COMPLETE_REJECT, "").strip()

    ai_timestamp = timezone.now().isoformat()

    # Append AI response to history
    chat_history.append(
        {
            "role": "ai",
            "text": clean_ai_text,
            "timestamp": ai_timestamp,
        }
    )

    # Save updated history
    interview.chat_history = chat_history
    update_fields = ["chat_history", "updated_at"]

    if is_complete:
        interview.status = Interview.Status.COMPLETED
        update_fields.append("status")

    interview.save(update_fields=update_fields)

    # If complete, run evaluation and update application status
    if is_complete:
        logger.info("Chat session %s (%s) completed, running evaluation...", interview.id, interview.session_type)

        try:
            evaluate_chat_interview(interview, ai_decision=ai_decision or "advance")
        except Exception as e:
            logger.error("Failed to evaluate session %s: %s", interview.id, e)

    return {
        "ai_message": clean_ai_text,
        "ai_timestamp": ai_timestamp,
        "is_complete": is_complete,
        "ai_decision": ai_decision,
        "chat_history": chat_history,
    }


def process_candidate_message(interview: Interview, candidate_message: str) -> dict:
    """
    Process a candidate's text message and generate the AI response.

    Returns dict with:
    - ai_message: str — the AI's response text (cleaned, no markers)
    - is_complete: bool — whether the session is now complete
    - ai_decision: str | None — "advance" or "reject" if complete
    - chat_history: list — updated chat history
    """
    now = timezone.now().isoformat()

    candidate_entry = {
        "role": "candidate",
        "text": candidate_message,
        "timestamp": now,
    }

    return _get_ai_response_and_update_history(interview, candidate_entry)


def process_voice_message(*, interview: Interview, audio_file, duration: float) -> dict:
    """
    Process a candidate's voice message: upload, transcribe, and generate AI response.

    Steps:
    1. Upload audio to S3 via upload_voice_message_to_s3
    2. Transcribe via transcribe_audio
    3. Append candidate voice message to chat_history with extra fields
    4. Get AI response via shared helper
    5. Return dict with: ai_message, candidate_transcript, candidate_audio_url

    Returns dict with:
    - ai_message: str
    - ai_timestamp: str
    - is_complete: bool
    - ai_decision: str | None
    - chat_history: list
    - candidate_transcript: str
    - candidate_audio_url: str
    """
    from apps.interviews.transcription_service import (
        transcribe_audio,
        upload_voice_message_to_s3,
    )

    # Read bytes once — the file object can't be re-read after S3 upload
    file_bytes = audio_file.read()
    filename = getattr(audio_file, "name", "audio.webm") or "audio.webm"

    # 1. Upload audio to S3
    import io

    s3_key = upload_voice_message_to_s3(
        file_obj=io.BytesIO(file_bytes),
        interview_id=str(interview.id),
        filename=filename,
    )

    # 2. Transcribe audio
    transcript = transcribe_audio(
        file_bytes=file_bytes,
        filename=filename,
    )

    now = timezone.now().isoformat()

    # 3. Build candidate entry with voice metadata
    candidate_entry = {
        "role": "candidate",
        "text": transcript,
        "timestamp": now,
        "message_type": "voice",
        "audio_url": s3_key,
        "duration": duration,
    }

    # 4. Get AI response using shared helper
    result = _get_ai_response_and_update_history(interview, candidate_entry)

    # 5. Augment result with voice-specific fields
    result["candidate_transcript"] = transcript
    result["candidate_audio_url"] = s3_key

    return result


def evaluate_chat_interview(interview: Interview, *, ai_decision: str = "advance") -> None:
    """
    Evaluate a completed chat session using GPT.

    Analyzes the full transcript and scores the candidate on each
    step-specific criteria. Saves scores, overall score, AI summary,
    and triggers the application status update via complete_session().
    """
    import json
    from decimal import Decimal

    from apps.interviews.models import InterviewScore
    from apps.interviews.services import complete_session

    client = _get_client()
    application = interview.application
    vacancy = application.vacancy
    step = interview.session_type

    # Build transcript text
    transcript_lines = []
    for msg in interview.chat_history or []:
        role_label = "Interviewer" if msg["role"] == "ai" else "Candidate"
        transcript_lines.append(f"{role_label}: {msg['text']}")
    transcript_text = "\n\n".join(transcript_lines)

    # Get criteria filtered by step
    criteria_list = list(
        vacancy.criteria.filter(step=step).order_by("order").values("id", "name", "description", "weight")
    )

    if not criteria_list:
        logger.warning("No criteria for vacancy %s step %s, skipping scoring", vacancy.id, step)
        # Still complete the session even without scoring
        complete_session(
            interview=interview,
            overall_score=Decimal("0"),
            ai_summary="No evaluation criteria configured.",
            transcript=interview.chat_history or [],
            ai_decision=ai_decision,
        )
        return

    criteria_json = json.dumps(
        [
            {"id": str(c["id"]), "name": c["name"], "description": c["description"], "weight": c["weight"]}
            for c in criteria_list
        ]
    )

    step_label = "prescanning" if step == Interview.SessionType.PRESCANNING else "interview"

    eval_prompt = f"""You are an expert HR evaluator. Analyze this {step_label} transcript and score the candidate.

## Position
{vacancy.title} at {vacancy.company.name}

## Job Description
{vacancy.description}

## Requirements
{vacancy.requirements or "Not specified"}

## Evaluation Criteria
{criteria_json}

## {step_label.title()} Transcript
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
        logger.error(
            "Failed to parse evaluation JSON for session %s. Raw response: %s",
            interview.id,
            raw[:500],
        )
        # Complete session with fallback so the pipeline doesn't get stuck
        complete_session(
            interview=interview,
            overall_score=Decimal("0"),
            ai_summary=str(MSG_EVALUATION_MALFORMED),
            transcript=interview.chat_history or [],
            ai_decision=ai_decision,
        )
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

    overall = result.get("overall_score", 0)
    overall_decimal = Decimal(str(min(10, max(0, float(overall)))))
    summary = result.get("summary", "")

    # Complete the session — this updates application status and creates interview if needed
    complete_session(
        interview=interview,
        overall_score=overall_decimal,
        ai_summary=summary,
        transcript=interview.chat_history or [],
        ai_decision=ai_decision,
    )

    logger.info(
        "Evaluation complete for session %s (%s): score=%.1f, decision=%s, %d criteria scored",
        interview.id,
        step,
        interview.overall_score or 0,
        ai_decision,
        len(score_objects),
    )
