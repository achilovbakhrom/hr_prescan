"""
AI chat screening service — handles conversation with candidates via Gemini.

Supports two session types:
- Prescanning: lighter, quicker initial screening (always chat mode)
- Interview: tougher, domain-specific evaluation (chat or meet mode)

Responsibilities:
- Build system prompt from vacancy + CV + questions (filtered by step)
- Generate AI greeting
- Process candidate messages and generate AI responses
- Detect when the session should end and AI decision (advance/reject)
- Trigger scoring/evaluation on completion
"""

from apps.interviews.chat_service.evaluation import evaluate_chat_interview
from apps.interviews.chat_service.messaging import (
    generate_greeting,
    process_candidate_message,
    process_voice_message,
)

__all__ = [
    "evaluate_chat_interview",
    "generate_greeting",
    "process_candidate_message",
    "process_voice_message",
]
