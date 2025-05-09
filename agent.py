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
            "You are a skilled, neutral interviewer exploring how people respond to narratives about quantum technologies. "
            "You begin by gently introducing several themes — cybersecurity, geopolitics, education, investment, ethics — without favoring any. "
            "Your goal is to see which ideas resonate with the participant and explore those further. "
            "If they seem unfamiliar, explain briefly and ask how that makes them feel or what they imagine. "
            "Be adaptive: if they mention encryption, ask about post-quantum risks; if they bring up global competition, ask about international relations. "
            "Always be open-ended, curious, and neutral — you're here to explore their thoughts, not guide them toward any conclusion."
        ),
        modalities=["audio", "text"],
        voice="echo",
    )

    agent = MultimodalAgent(model=model)
    await agent.start(ctx.room, participant)

    # ————— Opening script —————
    await agent.say(
        "Hi there! It’s really nice to meet you — thanks for joining. "
        "We’re having open conversations with people to hear how they imagine the future of technology, "
        "especially something called *quantum technologies*. That might sound a bit technical, but don’t worry — you don’t need any background in science. "
        "Quantum technologies use the strange behavior of very small particles to do things today's tech can’t — like ultra-secure communication, faster computing, or extremely precise sensors."
    )

    await agent.say(
        "These technologies show up in all kinds of places — from discussions about data privacy and global politics, "
        "to business investments, national strategies, or even school education. "
        "Some people think of them as revolutionary, others see risks. I'm curious: "
        "have you heard anything about quantum technologies in the news, at work, or just in conversation? What comes to mind?"
    )

    # From here, the bot responds based on input — using internal model adaptivity
    # No hardcoded follow-ups here, but the instructions above ensure adaptive follow-through
    # The next user response triggers theme-specific questioning automatically

if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
