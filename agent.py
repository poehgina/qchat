from __future__ import annotations
import sys
import logging
import os
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

# ————— Load environment variables —————
load_dotenv(dotenv_path=".env.local")

print("✅ OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
print("✅ Python interpreter:", sys.executable)
print("✅ dotenv is working!")

# ————— Logger setup —————
logger = logging.getLogger("quantum-interview-worker")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    await run_multimodal_agent(ctx, participant)

    logger.info("✅ Interview session started")


async def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("🔍 Launching quantum interview agent")

    model = openai.realtime.RealtimeModel(
        instructions=(
            "You are a skilled interviewer exploring public perceptions of quantum technologies. "
            "Your job is to understand what people know, imagine, and feel about these technologies — including "
            "quantum computing, sensing, and communication. "
            "Be curious, neutral, and conversational. Ask open-ended questions to uncover their knowledge, visions "
            "for the future, potential applications they foresee, and any risks or concerns. "
            "Start gently, adapt your tone to their knowledge level, and keep the conversation flowing naturally. "
            "Avoid sounding like a script — be warm, informal, and exploratory."
        ),
        modalities=["audio", "text"],
        voice="echo",
    )

    agent = MultimodalAgent(model=model)
    await agent.start(ctx.room, participant)

    await agent.say(
        "Hi there! It’s really nice to meet you. "
        "We’re having some open conversations with people to hear what they think about future technologies — "
        "especially quantum ones. That includes things like quantum computers, sensors, or communication systems. "
        "You don’t need to be an expert — I’m just curious to hear your thoughts. "
        "So, to start off casually: when you hear the phrase *quantum technology*, what comes to mind?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
