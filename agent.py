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
        "Hi there! It’s really nice to meet you — thanks for taking the time to chat. "
        "We’re having conversations with people to hear how they imagine the future of technology, "
        "especially something called *quantum technologies*. "
        "Now, that might sound a bit technical, but don’t worry — you don’t need any background in science to take part. "
        "Just to give a quick idea: quantum technologies use the unusual behavior of tiny particles — like atoms — "
        "to do things that aren’t possible with today’s tech. "
        "This includes quantum computing, which could solve really complex problems; "
        "quantum sensing, which can measure things with incredible precision; "
        "and quantum communication, which could make information-sharing much more secure. "
        "But what really matters here is what *you* think — there are no right or wrong answers. "
        "So to start us off: when you hear the phrase *quantum technology*, what comes to mind?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
