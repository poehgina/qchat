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
            "You are a skilled interviewer exploring how people think and feel about quantum technologies. "
            "Begin with a warm, open tone. Offer a short, accessible explanation of quantum technologies — including computing, sensing, and communication. "
            "Introduce the idea that these technologies are discussed in many ways — in business, politics, education, society, ethics — but do not emphasize any one theme. "
            "Ask what comes to mind for the participant when they hear about quantum tech. "
            "Then, based on what they mention, explore related themes such as cybersecurity, global rivalry, investment, education, ethics, gender, or environmental impact. "
            "Be adaptive, curious, and non-directive. If the participant doesn’t know about something, briefly explain it and ask how it makes them feel or what they imagine. "
            "You are here to understand what narratives or ideas resonate with them — not to inform or persuade."
        ),
        modalities=["audio", "text"],
        voice="echo",
    )

    agent = MultimodalAgent(model=model)
    await agent.start(ctx.room, participant)

    await agent.say(
        "Hi there! It's great to meet you — and thanks for taking the time to chat. "
        "We're having open conversations with people to explore how they think and feel about future technologies, "
        "especially something called *quantum technologies*. "
        "That might sound a bit complex, but don't worry — you don't need to be an expert or know any physics."
    )

    await agent.say(
        "Quantum technologies use the strange behavior of very small particles — like atoms — "
        "to do things that today’s tech can’t. This includes quantum computing, which could solve really complex problems, "
        "quantum sensing for extremely precise measurements, and quantum communication, which might make information sharing more secure."
    )

    await agent.say(
        "These technologies are being talked about in lots of ways — in business, in politics, in education, even in ethics and global cooperation. "
        "Some people talk about them as game-changers, others focus on risks or social impact. "
        "But what really matters here is what *you* think."
    )

    await agent.say(
        "So to start us off: when you hear the phrase *quantum technology*, what comes to mind?"
    )


if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
