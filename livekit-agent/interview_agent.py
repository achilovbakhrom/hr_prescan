"""VoicePipelineAgent configuration for AI interviews."""

import asyncio
import logging
import os
import time

from livekit.agents import llm, tokenize, tts as agents_tts
from livekit.agents.pipeline import AgentTranscriptionOptions, VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, google, silero
from livekit.plugins.elevenlabs import Voice, VoiceSettings

from conversation_control import ConversationControl
from context import fetch_interview_context
from evaluator import evaluate_interview
from integrity import IntegrityMonitor
from prompt import build_opening_message, build_system_prompt
from room_lifecycle import shutdown_after_final_response
from runtime_config import (
    ALLOW_CROSS_LANGUAGE_TTS_FALLBACK,
    DEEPGRAM_API_KEY,
    DEEPGRAM_ENDPOINTING_MS,
    DEEPGRAM_MODEL,
    DEEPGRAM_TTS_MODEL,
    ELEVENLABS_EXTENDED_MODEL,
    ELEVENLABS_MODEL,
    ELEVENLABS_SIMILARITY_BOOST,
    ELEVENLABS_SPEED,
    ELEVENLABS_STABILITY,
    ELEVENLABS_STYLE,
    INTERRUPT_MIN_WORDS,
    INTERRUPT_SPEECH_DURATION,
    MAX_ENDPOINTING_DELAY,
    MIN_ENDPOINTING_DELAY,
    PREEMPTIVE_SYNTHESIS,
    TTS_PROVIDER,
)
from speech_utils import speech_text

logger = logging.getLogger("interview-agent")

ELEVENLABS_DEFAULT_VOICE_ID = os.environ.get(
    "ELEVENLABS_VOICE_ID_DEFAULT",
    os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
)
ELEVENLABS_FALLBACK_VOICE_ID = os.environ.get(
    "ELEVENLABS_VOICE_ID_FALLBACK",
    "EXAVITQu4vr4xnSDxMaL",
)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

DEEPGRAM_TTS_MODELS_BY_LANGUAGE = {
    "de": "aura-2-viktoria-de",
    "en": "aura-2-vesta-en",
    "es": "aura-2-estrella-es",
    "fr": "aura-2-hector-fr",
}
ELEVENLABS_FLASH_LANGUAGES = {"ar", "ru", "tr", "uk"}
ELEVENLABS_EXTENDED_LANGUAGES = {"kk"}
ELEVENLABS_VOICE_IDS_BY_LANGUAGE = {
    "ar": os.environ.get("ELEVENLABS_VOICE_ID_AR", ""),
    "kk": os.environ.get("ELEVENLABS_VOICE_ID_KK", ""),
    "ru": os.environ.get("ELEVENLABS_VOICE_ID_RU", ""),
    "tr": os.environ.get("ELEVENLABS_VOICE_ID_TR", ""),
    "uk": os.environ.get("ELEVENLABS_VOICE_ID_UK", ""),
    "uz": os.environ.get("ELEVENLABS_VOICE_ID_UZ", ""),
}
ELEVENLABS_VOICE_LANGUAGE_FALLBACKS = {
    "kk": "ru",
    "uz": "ru",
}


def _deepgram_language(language: str) -> str:
    supported_languages = {"de", "en", "es", "fr", "ru", "uk"}
    return language if language in supported_languages else "multi"


def _deepgram_tts(model: str, *, use_streaming: bool):
    logger.info("Using Deepgram TTS provider with model %s.", model)
    provider = deepgram.TTS(
        model=model,
        api_key=DEEPGRAM_API_KEY or None,
        use_streaming=use_streaming,
    )
    if use_streaming:
        return provider
    return agents_tts.StreamAdapter(
        tts=provider,
        sentence_tokenizer=tokenize.basic.SentenceTokenizer(),
    )


def _deepgram_tts_for_language(language: str):
    model = DEEPGRAM_TTS_MODELS_BY_LANGUAGE.get(language)
    if model:
        return _deepgram_tts(model, use_streaming=False)
    return _deepgram_tts(DEEPGRAM_TTS_MODEL, use_streaming=True)


def _elevenlabs_model_for_language(language: str) -> str:
    if language in ELEVENLABS_EXTENDED_LANGUAGES:
        return ELEVENLABS_EXTENDED_MODEL
    return ELEVENLABS_MODEL


def _elevenlabs_voice_id_for_language(language: str) -> str:
    voice_id = ELEVENLABS_VOICE_IDS_BY_LANGUAGE.get(language)
    if voice_id:
        return voice_id

    fallback_language = ELEVENLABS_VOICE_LANGUAGE_FALLBACKS.get(language)
    if fallback_language:
        fallback_voice_id = ELEVENLABS_VOICE_IDS_BY_LANGUAGE.get(fallback_language)
        if fallback_voice_id:
            logger.info(
                "Using ElevenLabs %s voice for %s interview.",
                fallback_language,
                language,
            )
            return fallback_voice_id

    return ELEVENLABS_DEFAULT_VOICE_ID


def _masked_voice_id(voice_id: str) -> str:
    if len(voice_id) <= 8:
        return "configured"
    return f"{voice_id[:4]}...{voice_id[-4:]}"


def _elevenlabs_tts(language: str, *, voice_id: str | None = None, label: str = "language-specific"):
    model = _elevenlabs_model_for_language(language)
    selected_voice_id = voice_id or _elevenlabs_voice_id_for_language(language)
    logger.info(
        "Using ElevenLabs TTS provider with model %s and %s voice %s for %s.",
        model,
        label,
        _masked_voice_id(selected_voice_id),
        language,
    )
    return elevenlabs.TTS(
        model=model,
        api_key=ELEVENLABS_API_KEY,
        voice=Voice(
            id=selected_voice_id,
            name="Interviewer",
            category="premade",
            settings=VoiceSettings(
                stability=ELEVENLABS_STABILITY,
                similarity_boost=ELEVENLABS_SIMILARITY_BOOST,
                style=ELEVENLABS_STYLE,
                speed=ELEVENLABS_SPEED,
                use_speaker_boost=True,
            ),
        ),
    )


def _elevenlabs_supports_language(language: str) -> bool:
    return language in ELEVENLABS_FLASH_LANGUAGES or language in ELEVENLABS_EXTENDED_LANGUAGES


def _tts_with_optional_english_fallback(language: str):
    primary = _elevenlabs_tts(language)
    if not ALLOW_CROSS_LANGUAGE_TTS_FALLBACK:
        logger.info("Cross-language TTS fallback disabled for %s.", language)
        return primary

    fallback_voice = _elevenlabs_tts(
        language,
        voice_id=ELEVENLABS_FALLBACK_VOICE_ID,
        label="premade recovery",
    )
    logger.warning(
        "No native Deepgram TTS model for %s. Falling back to ElevenLabs premade voice only if the configured voice fails.",
        language,
    )
    return agents_tts.FallbackAdapter(
        [primary, fallback_voice],
        max_retry_per_tts=0,
        attempt_timeout=6.0,
    )


def _build_tts(language: str):
    if TTS_PROVIDER == "deepgram":
        return _deepgram_tts_for_language(language)

    if TTS_PROVIDER == "elevenlabs":
        return _elevenlabs_tts(language)

    if TTS_PROVIDER != "auto":
        logger.warning("Unknown TTS_PROVIDER=%s. Using automatic TTS selection.", TTS_PROVIDER)

    deepgram_model = DEEPGRAM_TTS_MODELS_BY_LANGUAGE.get(language)
    if deepgram_model:
        return _deepgram_tts_for_language(language)

    if ELEVENLABS_API_KEY and _elevenlabs_supports_language(language):
        return _tts_with_optional_english_fallback(language)

    logger.warning(
        "No reliable native TTS provider configured for %s. Falling back to English TTS.",
        language,
    )
    return _deepgram_tts_for_language("en")


async def create_interview_agent(ctx) -> VoicePipelineAgent:
    """Create and configure the interview agent for a room."""
    # Fetch interview context (vacancy, questions, CV data)
    context = await fetch_interview_context(room_name=ctx.room.name)
    logger.info("Interview %s resolved language: %s", context.interview_id, context.language)

    # Build system prompt
    system_prompt = build_system_prompt(context=context)
    chat_ctx = llm.ChatContext().append(role="system", text=system_prompt)

    # Configure STT (Speech-to-Text)
    stt = deepgram.STT(
        model=DEEPGRAM_MODEL,
        language=_deepgram_language(context.language),
        interim_results=True,
        punctuate=True,
        no_delay=True,
        endpointing_ms=DEEPGRAM_ENDPOINTING_MS,
    )

    # Configure LLM
    gemini_llm = google.LLM(
        model=GEMINI_MODEL,
        api_key=GOOGLE_API_KEY,
        temperature=0.35,
    )

    # Configure TTS (Text-to-Speech)
    tts = _build_tts(context.language)

    control = ConversationControl()

    async def _before_llm_cb(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
        instruction = control.instruction()
        if instruction:
            chat_ctx.messages.append(
                llm.ChatMessage.create(role="system", text=instruction)
            )
        return agent.llm.chat(chat_ctx=chat_ctx, fnc_ctx=agent.fnc_ctx)

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=stt,
        llm=gemini_llm,
        tts=tts,
        chat_ctx=chat_ctx,
        allow_interruptions=True,
        interrupt_speech_duration=INTERRUPT_SPEECH_DURATION,
        interrupt_min_words=INTERRUPT_MIN_WORDS,
        min_endpointing_delay=MIN_ENDPOINTING_DELAY,
        max_endpointing_delay=MAX_ENDPOINTING_DELAY,
        preemptive_synthesis=PREEMPTIVE_SYNTHESIS,
        transcription=AgentTranscriptionOptions(
            user_transcription=True,
            agent_transcription=True,
            agent_transcription_speed=1.1,
        ),
        before_llm_cb=_before_llm_cb,
    )
    agent.hr_prescan_opening_message = build_opening_message(context=context)

    # Collect transcript entries during the interview
    transcript: list[dict] = []

    # Initialise integrity monitor
    interview_start_time = time.time()
    monitor = IntegrityMonitor(interview_start_time=interview_start_time)
    shutdown_task: asyncio.Task | None = None

    def _schedule_shutdown() -> None:
        nonlocal shutdown_task
        if shutdown_task and not shutdown_task.done():
            return
        shutdown_task = asyncio.create_task(shutdown_after_final_response(ctx, agent))

    @agent.on("user_speech_committed")
    def _on_user_speech(message) -> None:
        text = speech_text(message)
        if not text:
            return
        control.record_candidate(text)
        transcript.append(
            {
                "speaker": "candidate",
                "text": text,
                "timestamp": round(time.time() - interview_start_time, 2),
            }
        )
        # Feed transcript into integrity monitor for audio anomaly detection
        monitor.add_transcript_entry(speaker="candidate", text=text)

    @agent.on("agent_speech_committed")
    def _on_agent_speech(message) -> None:
        text = speech_text(message)
        if not text:
            return
        control.record_interviewer(text)
        transcript.append(
            {
                "speaker": "interviewer",
                "text": text,
                "timestamp": round(time.time() - interview_start_time, 2),
            }
        )
        monitor.add_transcript_entry(speaker="interviewer", text=text)
        if control.should_shutdown_after_interviewer():
            _schedule_shutdown()

    async def _on_shutdown(reason: str = "") -> None:
        """Stop monitoring, evaluate, and send results when the LiveKit job ends."""
        # Stop integrity monitor and collect flags
        integrity_flags = await monitor.stop()
        logger.info(
            "Integrity monitoring stopped for interview %s. Reason: %s. Flags: %d",
            context.interview_id,
            reason or "unknown",
            len(integrity_flags),
        )

        if not transcript:
            logger.warning(
                "Interview %s ended with empty transcript.", context.interview_id
            )
            return

        logger.info(
            "Interview %s ended. Evaluating %d transcript entries.",
            context.interview_id,
            len(transcript),
        )
        try:
            await evaluate_interview(
                interview_id=context.interview_id,
                transcript=transcript,
                criteria=context.criteria,
                cv_summary=context.cv_summary,
                language=context.language,
                integrity_flags=integrity_flags,
            )
        except Exception:
            logger.exception(
                "Failed to evaluate interview %s.",
                context.interview_id,
            )

    ctx.add_shutdown_callback(_on_shutdown)
    monitor.start()
    logger.info("Integrity monitoring started for interview %s.", context.interview_id)

    return agent
