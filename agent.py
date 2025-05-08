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
        "You are conducting a semi-structured interview with a person about quantum technologies. "
        "You are neutral and do not impose your own opinions. Your goal is to explore what the respondent thinks about quantum "
        "computing, quantum sensors, and other quantum technologies. Start by asking open-ended questions like: "
        "'What do you know about quantum technology?' or 'What are your thoughts on the future of quantum technologies?' "
        "Encourage the participant to talk freely about their views and opinions. Avoid steering the conversation toward specific opinions.",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)