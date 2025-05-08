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
    logger.info("Starting Globi-style agent")

    model = openai.realtime.RealtimeModel(
        instructions=(
            "You are Globi, the famous Swiss children's character – a blue parrot who’s curious, joyful, "
            "and full of wonder. You speak in cheerful Swiss German (Züridütsch) as if you’re telling a story "
            "or going on an adventure. You love to ask playful questions and imagine things. You use words like "
            "'juhui!', 'so spannend!', 'mega gluschtig', and 'chunnt mir spanisch vor!'. You are interviewing "
            "someone about quantum technology like it's a big magical mystery you’re excited to learn about. "
            "Be kind, open-hearted, a little silly – and always curious!"
        ),
        modalities=["audio", "text"],
        voice="echo",  # Best for clear, expressive tone
    )

    agent = MultimodalAgent(model=model)
    await agent.start(ctx.room, participant)

    await agent.say(
        "Hoi zäme! Ich bi de Globi – und hüt gönd mir zäme es bitzeli entdecke, gäll? "
        "S’Thema heisst Quantum Technology… wow! Es tönt e chli wie Zauberei, oder? "
        "Hesch du scho öppis devon ghört? Oder isch das für dich eher wie e Geheimsprache us em Weltall?",
        allow_interruptions=True
    )


if __name__ == "__main__":
    # Create and run worker with entrypoint
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
