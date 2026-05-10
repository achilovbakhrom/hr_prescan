"""VoicePipelineAgent configuration for AI interviews."""

import asyncio
import logging
import os
import time

from livekit.agents import llm
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
    DEEPGRAM_ENDPOINTING_MS,
    DEEPGRAM_MODEL,
    ELEVENLABS_MODEL,
    ELEVENLABS_SIMILARITY_BOOST,
    ELEVENLABS_SPEED,
    ELEVENLABS_STABILITY,
    ELEVENLABS_STYLE,
    MAX_ENDPOINTING_DELAY,
    MIN_ENDPOINTING_DELAY,
)
from speech_utils import speech_text

logger = logging.getLogger("interview-agent")

ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")


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
        language="multi",  # EN/RU code-switching support
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
    tts = elevenlabs.TTS(
        model=ELEVENLABS_MODEL,
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
        min_endpointing_delay=MIN_ENDPOINTING_DELAY,
        max_endpointing_delay=MAX_ENDPOINTING_DELAY,
        preemptive_synthesis=True,
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
