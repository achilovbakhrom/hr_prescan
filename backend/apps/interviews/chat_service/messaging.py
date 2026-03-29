"""Message processing — greeting, text messages, voice messages, AI response generation."""

import logging

from django.conf import settings
from django.utils import timezone
from google.genai import types

from apps.interviews.chat_service._constants import (
    SESSION_COMPLETE_ADVANCE,
    SESSION_COMPLETE_REJECT,
    get_client,
)
from apps.interviews.chat_service.prompts import build_system_prompt
from apps.interviews.models import Interview

logger = logging.getLogger(__name__)


def generate_greeting(interview: Interview) -> str:
    """Generate the AI's opening message for a chat session."""
    client = get_client()
    system_prompt = build_system_prompt(interview)

    step_label = "prescanning" if interview.session_type == Interview.SessionType.PRESCANNING else "interview"

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=
                    f"[SYSTEM: The candidate has just opened the {step_label} chat. "
                    "Send a brief, warm greeting (2-3 sentences). Introduce yourself and "
                    "the company briefly if company info is available. Then ask the candidate "
                    "to tell you about themselves.]"
                )],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=system_prompt,
            max_output_tokens=300,
            temperature=0.7,
        ),
    )

    greeting = response.text or ""
    # Remove completion markers from greeting (safety check)
    greeting = greeting.replace(SESSION_COMPLETE_ADVANCE, "").replace(SESSION_COMPLETE_REJECT, "").strip()
    return greeting


def _get_ai_response_and_update_history(interview: Interview, candidate_entry: dict) -> dict:
    """Append candidate entry to history, call Gemini, handle markers, save, evaluate."""
    from apps.interviews.chat_service.evaluation import evaluate_chat_interview

    client = get_client()
    system_prompt = build_system_prompt(interview)

    # Build conversation history for Gemini
    chat_history = list(interview.chat_history or [])
    chat_history.append(candidate_entry)

    # Convert our chat history to Gemini content format
    gemini_contents = []
    for msg in chat_history:
        role = "model" if msg["role"] == "ai" else "user"
        gemini_contents.append(
            types.Content(role=role, parts=[types.Part(text=msg["text"])])
        )

    # Call Gemini
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=system_prompt,
            max_output_tokens=400,
            temperature=0.7,
        ),
    )

    raw_ai_text = response.text or ""

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
    chat_history.append({
        "role": "ai",
        "text": clean_ai_text,
        "timestamp": ai_timestamp,
    })

    # Save updated history
    interview.chat_history = chat_history
    update_fields = ["chat_history", "updated_at"]
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
    """Process a candidate's text message and generate the AI response."""
    now = timezone.now().isoformat()

    candidate_entry = {
        "role": "candidate",
        "text": candidate_message,
        "timestamp": now,
    }

    return _get_ai_response_and_update_history(interview, candidate_entry)


def process_voice_message(*, interview: Interview, audio_file, duration: float) -> dict:
    """Process a candidate's voice message: upload to S3, transcribe, get AI response."""
    import io

    from apps.interviews.transcription_service import (
        transcribe_audio,
        upload_voice_message_to_s3,
    )

    # Read bytes once — the file object can't be re-read after S3 upload
    file_bytes = audio_file.read()
    filename = getattr(audio_file, "name", "audio.webm") or "audio.webm"

    # 1. Upload audio to S3
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
