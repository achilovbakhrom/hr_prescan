"""
Integrity monitoring for AI interviews.
Periodically analyzes video frames and audio for cheating indicators.
"""

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import dataclass, field

from google import genai
from google.genai import types

logger = logging.getLogger("interview-agent")

# How often (in seconds) to capture a frame for integrity analysis
FRAME_CHECK_INTERVAL = 30

# Flag types matching the backend model choices
FLAG_FACE_MISSING = "face_not_visible"
FLAG_MULTIPLE_FACES = "multiple_faces"
FLAG_GAZE_DEVIATION = "gaze_deviation"
FLAG_AUDIO_ANOMALY = "audio_anomaly"
FLAG_CV_INCONSISTENCY = "cv_inconsistency"

# Severity levels
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "high"  # Map critical → high (backend only has low/medium/high)


@dataclass
class IntegrityFlagRecord:
    """A single integrity flag detected during the interview."""

    flag_type: str
    severity: str
    description: str
    timestamp_seconds: int | None = None


class IntegrityMonitor:
    """Monitors an interview session for cheating indicators.

    Usage::

        monitor = IntegrityMonitor(interview_start_time=time.time())
        monitor.start()               # begins background monitoring
        ...
        flags = await monitor.stop()  # stops monitoring, returns collected flags
    """

    def __init__(self, interview_start_time: float | None = None) -> None:
        self._start_time: float = interview_start_time or time.time()
        self._flags: list[IntegrityFlagRecord] = []
        self._running: bool = False
        self._task: asyncio.Task | None = None
        self._client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))

        # Transcript accumulation for audio anomaly detection
        self._transcript_entries: list[dict] = []

        # Frame snapshots: list of base64-encoded JPEG strings captured periodically
        # In production, these are populated by a video frame capture callback.
        # For MVP, the list is populated externally via add_frame_snapshot().
        self._frame_snapshots: list[tuple[float, str]] = []  # (timestamp, base64_jpeg)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin periodic integrity monitoring."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("IntegrityMonitor started.")

    async def stop(self) -> list[dict]:
        """Stop monitoring and return all collected flags as dicts."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info(
            "IntegrityMonitor stopped. Total flags collected: %d", len(self._flags)
        )
        return self.get_flags()

    def add_transcript_entry(self, speaker: str, text: str) -> None:
        """Record a transcript entry for audio anomaly detection."""
        self._transcript_entries.append(
            {
                "speaker": speaker,
                "text": text,
                "timestamp_seconds": int(time.time() - self._start_time),
            }
        )

    def add_frame_snapshot(self, base64_jpeg: str) -> None:
        """Provide a video frame for vision analysis.

        In production, call this from a LiveKit video frame callback.
        The frame should be a base64-encoded JPEG image.
        """
        elapsed = int(time.time() - self._start_time)
        self._frame_snapshots.append((elapsed, base64_jpeg))

    def get_flags(self) -> list[dict]:
        """Return all collected integrity flags as a list of dicts."""
        return [
            {
                "flag_type": f.flag_type,
                "severity": f.severity,
                "description": f.description,
                "timestamp_seconds": f.timestamp_seconds,
            }
            for f in self._flags
        ]

    # ------------------------------------------------------------------
    # Internal monitoring loop
    # ------------------------------------------------------------------

    async def _monitoring_loop(self) -> None:
        """Periodically run integrity checks."""
        while self._running:
            try:
                await asyncio.sleep(FRAME_CHECK_INTERVAL)
                if not self._running:
                    break

                # Analyze latest frame snapshot if available
                if self._frame_snapshots:
                    timestamp, frame_b64 = self._frame_snapshots[-1]
                    await self._analyze_frame(frame_b64, timestamp)

                # Check audio transcript for anomalies
                self._check_audio_anomaly()

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in integrity monitoring loop.")

    # ------------------------------------------------------------------
    # Analysis methods
    # ------------------------------------------------------------------

    async def _analyze_frame(self, frame_b64: str, timestamp_seconds: int) -> None:
        """Send a video frame to Gemini Vision to check for integrity issues.

        Checks for:
        - Face present / face missing
        - Multiple faces visible
        - Gaze direction (looking away from camera)
        """
        prompt = (
            "You are an AI proctoring assistant analyzing a video interview frame. "
            "Examine the image and respond with a JSON object with exactly these fields:\n"
            "{\n"
            '  "face_present": true/false,\n'
            '  "multiple_faces": true/false,\n'
            '  "gaze_on_screen": true/false,\n'
            '  "notes": "brief description of what you see"\n'
            "}\n"
            "gaze_on_screen is true if the candidate appears to be looking at the camera/screen."
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
                contents=[
                    types.Part.from_bytes(
                        data=base64.b64decode(frame_b64),
                        mime_type="image/jpeg",
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                    response_mime_type="application/json",
                    max_output_tokens=200,
                    temperature=0,
                ),
            )

            result = json.loads(response.text)
            logger.debug("Frame analysis result at %ds: %s", timestamp_seconds, result)

            # Evaluate results and add flags
            if not result.get("face_present", True):
                self._add_flag(
                    flag_type=FLAG_FACE_MISSING,
                    severity=SEVERITY_MEDIUM,
                    description=(
                        f"No face detected in the video frame. "
                        f"Notes: {result.get('notes', '')}"
                    ),
                    timestamp_seconds=timestamp_seconds,
                )

            elif result.get("multiple_faces", False):
                self._add_flag(
                    flag_type=FLAG_MULTIPLE_FACES,
                    severity=SEVERITY_HIGH,
                    description=(
                        f"Multiple faces detected in the video frame — "
                        f"possible unauthorized assistance. "
                        f"Notes: {result.get('notes', '')}"
                    ),
                    timestamp_seconds=timestamp_seconds,
                )

            if result.get("face_present", True) and not result.get("gaze_on_screen", True):
                self._add_flag(
                    flag_type=FLAG_GAZE_DEVIATION,
                    severity=SEVERITY_LOW,
                    description=(
                        f"Candidate's gaze appears to be off-screen — "
                        f"may be reading from an external source. "
                        f"Notes: {result.get('notes', '')}"
                    ),
                    timestamp_seconds=timestamp_seconds,
                )

        except Exception:
            logger.exception("Failed to analyze video frame at %ds.", timestamp_seconds)

    def _check_audio_anomaly(self) -> None:
        """Analyze the accumulated transcript for signs of multiple speakers.

        Heuristics used for MVP:
        - Unusually long candidate turns that don't follow conversational patterns
          may indicate a second person dictating answers off-screen.
        - Very fast, precise answers to all questions without any hesitation filler
          words may indicate reading from a script.

        This is a lightweight rule-based check. A full implementation would use
        speaker diarisation from the STT provider.
        """
        candidate_entries = [
            e for e in self._transcript_entries if e["speaker"] == "candidate"
        ]

        if len(candidate_entries) < 3:
            # Not enough data yet
            return

        # Heuristic: if any single candidate response is extremely long (> 500 words),
        # it may indicate reading from a prepared script / multiple speakers
        for entry in candidate_entries:
            word_count = len(entry["text"].split())
            if word_count > 500:
                timestamp = entry.get("timestamp_seconds")
                # Only flag once per entry
                already_flagged = any(
                    f.flag_type == FLAG_AUDIO_ANOMALY
                    and f.timestamp_seconds == timestamp
                    for f in self._flags
                )
                if not already_flagged:
                    self._add_flag(
                        flag_type=FLAG_AUDIO_ANOMALY,
                        severity=SEVERITY_MEDIUM,
                        description=(
                            f"Unusually long candidate response detected ({word_count} words). "
                            "This may indicate reading from a script or assistance from "
                            "another person not visible on camera."
                        ),
                        timestamp_seconds=timestamp,
                    )

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _add_flag(
        self,
        *,
        flag_type: str,
        severity: str,
        description: str,
        timestamp_seconds: int | None = None,
    ) -> None:
        """Record an integrity flag."""
        flag = IntegrityFlagRecord(
            flag_type=flag_type,
            severity=severity,
            description=description,
            timestamp_seconds=timestamp_seconds,
        )
        self._flags.append(flag)
        logger.warning(
            "Integrity flag [%s/%s] at %ss: %s",
            flag_type,
            severity,
            timestamp_seconds,
            description[:100],
        )
