"""LiveKit AI Interview Agent — entry point."""

import asyncio
import logging

from livekit.agents import WorkerOptions, cli

from interview_agent import create_interview_agent

logger = logging.getLogger("interview-agent")


async def entrypoint(ctx) -> None:
    """Called when a new interview room is created."""
    logger.info("Agent joining room: %s", ctx.room.name)
    agent = await create_interview_agent(ctx)
    await agent.start()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
