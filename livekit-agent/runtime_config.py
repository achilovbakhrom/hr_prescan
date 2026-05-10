"""Runtime tuning for the LiveKit interview agent."""

import os


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name) or str(default))


def env_int(name: str, default: int) -> int:
    return int(os.environ.get(name) or str(default))


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")
DEEPGRAM_MODEL = os.environ.get("DEEPGRAM_MODEL") or "nova-3"
DEEPGRAM_ENDPOINTING_MS = env_int("DEEPGRAM_ENDPOINTING_MS", 900)
MIN_ENDPOINTING_DELAY = env_float("LIVEKIT_MIN_ENDPOINTING_DELAY", 0.7)
MAX_ENDPOINTING_DELAY = env_float("LIVEKIT_MAX_ENDPOINTING_DELAY", 3.0)
INTERRUPT_SPEECH_DURATION = env_float("LIVEKIT_INTERRUPT_SPEECH_DURATION", 0.9)
INTERRUPT_MIN_WORDS = env_int("LIVEKIT_INTERRUPT_MIN_WORDS", 2)
PREEMPTIVE_SYNTHESIS = env_bool("LIVEKIT_PREEMPTIVE_SYNTHESIS", False)

TTS_PROVIDER = (os.environ.get("TTS_PROVIDER") or "auto").strip().lower()
DEEPGRAM_TTS_MODEL = os.environ.get("DEEPGRAM_TTS_MODEL") or "aura-asteria-en"
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL") or "eleven_flash_v2_5"
ELEVENLABS_EXTENDED_MODEL = os.environ.get("ELEVENLABS_EXTENDED_MODEL") or "eleven_v3"
ELEVENLABS_STABILITY = env_float("ELEVENLABS_STABILITY", 0.48)
ELEVENLABS_SIMILARITY_BOOST = env_float("ELEVENLABS_SIMILARITY_BOOST", 0.78)
ELEVENLABS_STYLE = env_float("ELEVENLABS_STYLE", 0.28)
ELEVENLABS_SPEED = env_float("ELEVENLABS_SPEED", 0.96)
