"""Room lifecycle helpers for ending interviews cleanly."""

import asyncio
import inspect
import logging

logger = logging.getLogger("interview-agent")


async def shutdown_after_final_response(ctx, agent, *, delay_seconds: float = 2.0) -> None:
    """Let final TTS finish, then close the agent session."""
    await asyncio.sleep(delay_seconds)
    close = getattr(agent, "aclose", None) or getattr(agent, "close", None)
    if callable(close):
        try:
            result = close()
            if inspect.isawaitable(result):
                await result
        except Exception:
            logger.exception("Failed to close interview agent before shutdown.")

    shutdown = getattr(ctx, "shutdown", None)
    if callable(shutdown):
        try:
            result = shutdown(reason="interview_completed")
            if inspect.isawaitable(result):
                await result
        except TypeError:
            result = shutdown("interview_completed")
            if inspect.isawaitable(result):
                await result
        return

    logger.warning("LiveKit JobContext does not expose shutdown().")
