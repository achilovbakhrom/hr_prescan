"""LiveKit AI Interview Agent — entry point."""

import logging

from livekit.agents import AutoSubscribe, WorkerOptions, cli

from interview_agent import create_interview_agent

logger = logging.getLogger("interview-agent")


async def entrypoint(ctx) -> None:
    """Called when a new interview room is created."""
    logger.info("Agent joining room: %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    agent = await create_interview_agent(ctx)
    agent.start(ctx.room)
    opening_message = getattr(agent, "hr_prescan_opening_message", "")
    if opening_message:
        await agent.say(opening_message, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
