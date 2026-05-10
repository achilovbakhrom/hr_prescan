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

ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

DEEPGRAM_TTS_MODELS_BY_LANGUAGE = {
    "de": "aura-2-viktoria-de",
    "en": "aura-2-thalia-en",
    "es": "aura-2-nestor-es",
    "fr": "aura-2-hector-fr",
}
ELEVENLABS_EXTENDED_LANGUAGES = {"kk"}


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


def _elevenlabs_tts(language: str):
    model = ELEVENLABS_EXTENDED_MODEL if language in ELEVENLABS_EXTENDED_LANGUAGES else ELEVENLABS_MODEL
    logger.info("Using ElevenLabs TTS provider with model %s.", model)
    return elevenlabs.TTS(
        model=model,
        api_key=ELEVENLABS_API_KEY,
        voice=Voice(
            id=ELEVENLABS_VOICE_ID,
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


def _build_tts(language: str):
    if TTS_PROVIDER == "deepgram":
        return _deepgram_tts_for_language(language)

    if TTS_PROVIDER == "elevenlabs":
        return agents_tts.FallbackAdapter(
            [_elevenlabs_tts(language), _deepgram_tts_for_language(language)],
            max_retry_per_tts=0,
            attempt_timeout=6.0,
        )

    if TTS_PROVIDER != "auto":
        logger.warning("Unknown TTS_PROVIDER=%s. Using automatic TTS selection.", TTS_PROVIDER)

    deepgram_model = DEEPGRAM_TTS_MODELS_BY_LANGUAGE.get(language)
    if deepgram_model:
        return _deepgram_tts_for_language(language)

    if ELEVENLABS_API_KEY:
        return agents_tts.FallbackAdapter(
            [_elevenlabs_tts(language), _deepgram_tts_for_language(language)],
            max_retry_per_tts=0,
            attempt_timeout=6.0,
        )

    logger.warning("No ElevenLabs API key for %s TTS. Falling back to Deepgram English TTS.", language)
    return _deepgram_tts_for_language(language)


async def create_interview_agent(ctx) -> VoicePipelineAgent:
    """Create and configure the interview agent for a room."""
    # Fetch interview context (vacancy, questions, CV data)
    context = await fetch_interview_context(room_name=ctx.room.name)

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
        temperature=0.7,
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
    monitor = IntegrityMonitor(interview_start_time=time.time())
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
        transcript.append({"speaker": "candidate", "text": text})
        # Feed transcript into integrity monitor for audio anomaly detection
        monitor.add_transcript_entry(speaker="candidate", text=text)

    @agent.on("agent_speech_committed")
    def _on_agent_speech(message) -> None:
        text = speech_text(message)
        if not text:
            return
        control.record_interviewer(text)
        transcript.append({"speaker": "interviewer", "text": text})
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
