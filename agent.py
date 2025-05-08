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

print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
print("Python interpreter:", sys.executable)
print("✅ dotenv is working!")

# ————— Logger setup —————
logger = logging.getLogger("my-worker")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    await run_multimodal_agent(ctx, participant)

    logger.info("Agent started")


async def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("Starting quantum interview agent")

    model = openai.realtime.RealtimeModel(
        instructions=(
            "You are an expert in conducting semi-structured interviews. Your goal is to investigate what "
            "imaginaries and visions people have about quantum technologies, without imposing any specific views on them. "
            "Focus on being neutral, empathetic, and open-ended in your approach. You should ask open-ended questions "
            "that encourage reflection and exploration. Be sure to respect the respondent's opinions and avoid leading "
            "them toward specific answers. Your role is to facilitate a thoughtful, unbiased exploration of their "
            "perceptions of quantum technologies, such as quantum computing, quantum sensors, or quantum imaging."
        ),
        modalities=["audio", "text"],
        voice="echo",
    )

    agent = MultimodalAgent(model=model)
    await agent.start(ctx.room, participant)

    await agent.say(
        "Hi there! I'm really glad you're here. I'm doing some interviews to learn what people think about quantum technologies. "
        "Don’t worry — you don’t need to be a scientist or know a lot about it. I'm just curious to hear your thoughts. "
        "Let’s start simple: when you hear the words *quantum technology*, what comes to mind for you? "
        "Have you heard of things like quantum computing or quantum sensors before?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)