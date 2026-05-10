"""Runtime tuning for the LiveKit interview agent."""

import os


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name) or str(default))


def env_int(name: str, default: int) -> int:
    return int(os.environ.get(name) or str(default))


DEEPGRAM_MODEL = os.environ.get("DEEPGRAM_MODEL") or "nova-3"
DEEPGRAM_ENDPOINTING_MS = env_int("DEEPGRAM_ENDPOINTING_MS", 50)
MIN_ENDPOINTING_DELAY = env_float("LIVEKIT_MIN_ENDPOINTING_DELAY", 0.05)
MAX_ENDPOINTING_DELAY = env_float("LIVEKIT_MAX_ENDPOINTING_DELAY", 0.6)

ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL") or "eleven_flash_v2_5"
ELEVENLABS_STABILITY = env_float("ELEVENLABS_STABILITY", 0.48)
ELEVENLABS_SIMILARITY_BOOST = env_float("ELEVENLABS_SIMILARITY_BOOST", 0.78)
ELEVENLABS_STYLE = env_float("ELEVENLABS_STYLE", 0.28)
ELEVENLABS_SPEED = env_float("ELEVENLABS_SPEED", 0.96)
