"""VoicePipelineAgent configuration for AI interviews."""

import logging
import os

from livekit.agents import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, openai

from context import fetch_interview_context
from evaluator import evaluate_interview
from prompt import build_system_prompt

logger = logging.getLogger("interview-agent")

ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


async def create_interview_agent(ctx) -> VoicePipelineAgent:
    """Create and configure the interview agent for a room."""
    # Fetch interview context (vacancy, questions, CV data)
    context = await fetch_interview_context(room_name=ctx.room.name)

    # Build system prompt
    system_prompt = build_system_prompt(context=context)

    # Configure STT (Speech-to-Text)
    stt = deepgram.STT(
        model="nova-2",
        language="multi",  # EN/RU code-switching support
    )

    # Configure LLM
    llm = openai.LLM(
        model="gpt-4o-mini",
        temperature=0.7,
    )

    # Configure TTS (Text-to-Speech)
    tts = elevenlabs.TTS(
        model="eleven_flash_v2_5",
        voice_id=ELEVENLABS_VOICE_ID,
    )

    agent = VoicePipelineAgent(
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=system_prompt,
    )

    # Collect transcript entries during the interview
    transcript: list[dict] = []

    @agent.on("user_speech_committed")
    def _on_user_speech(text: str) -> None:
        transcript.append({"speaker": "candidate", "text": text})

    @agent.on("agent_speech_committed")
    def _on_agent_speech(text: str) -> None:
        transcript.append({"speaker": "interviewer", "text": text})

    @agent.on("agent_stopped")
    async def _on_stopped() -> None:
        """Triggered when the interview ends — evaluate and send results."""
        if not transcript:
            logger.warning("Interview %s ended with empty transcript.", context.interview_id)
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
            )
        except Exception:
            logger.exception(
                "Failed to evaluate interview %s.", context.interview_id,
            )

    return agent
