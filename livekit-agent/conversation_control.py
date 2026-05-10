"""Deterministic conversation controls for the voice interviewer."""

from __future__ import annotations

import re


STOP_PATTERNS = (
    r"\b(can|could|should)\s+(we\s+)?(finish|stop|end)\b",
    r"\b(let'?s|lets)\s+(finish|stop|end)\b",
    r"\b(i\s+)?don'?t\s+want\s+to\s+(continue|pass|do)\b",
    r"\bnot\s+(a\s+)?(fit|match|for\s+me)\b",
    r"\bwrong\s+(role|profession|job|vacancy)\b",
    r"\bnot\s+(a\s+)?(cs\s*go|counter[- ]?strike).{0,24}(player|gamer)\b",
    r"\b(i\s+)?(am|m)\s+not\s+(a\s+)?(cs\s*go|counter[- ]?strike).{0,24}(player|gamer)\b",
    r"\bзаконч",
    r"\bостанов",
    r"\bне\s+хочу\s+(продолж|проход)",
    r"\bне\s+(подхожу|подходит|мой|моя)\b",
    r"\bне\s+игрок\b",
    r"\bдругая\s+професс",
)

LOW_FIT_PATTERNS = (
    r"\b(i\s+)?don'?t\s+know\b",
    r"\bno\s+experience\b",
    r"\bnever\s+(played|worked|used|done)\b",
    r"\bnot\s+familiar\b",
    r"\bnot\s+sure\b",
    r"\bcan'?t\s+answer\b",
    r"\bне\s+знаю\b",
    r"\bнет\s+опыта\b",
    r"\bникогда\s+не\s+(играл|работал|использовал)\b",
    r"\bне\s+знаком\b",
)

FINAL_WORD_PATTERNS = (
    r"\bfinal\s+(word|words|comment|comments)\b",
    r"\banything\s+(else|you'?d\s+like)\b",
    r"\blast\s+(word|thing)\b",
    r"\bпоследн",
    r"\bчто.*(добавить|сказать).*(hr|эйчар|рекрутер)",
)


class ConversationControl:
    """Track hard-stop conditions that the LLM prompt alone may ignore."""

    def __init__(self) -> None:
        self.candidate_turns = 0
        self.low_fit_signals = 0
        self.early_finish_requested = False
        self.final_words_requested = False
        self.final_words_answered = False

    def record_candidate(self, text: str) -> None:
        normalized = _normalize(text)
        if not normalized:
            return
        self.candidate_turns += 1
        if _matches_any(normalized, STOP_PATTERNS):
            self.early_finish_requested = True
        if _matches_any(normalized, LOW_FIT_PATTERNS):
            self.low_fit_signals += 1
        if self.final_words_requested:
            self.final_words_answered = True

    def record_interviewer(self, text: str) -> None:
        normalized = _normalize(text)
        if _matches_any(normalized, FINAL_WORD_PATTERNS):
            self.final_words_requested = True

    def instruction(self) -> str:
        if self.final_words_answered:
            return (
                "Hard conversation-control instruction: the candidate has already given final words. "
                "Thank them in one short sentence, say HR will review the interview, and stop. "
                "Do not ask another interview question."
            )

        if self.early_finish_requested:
            return (
                "Hard conversation-control instruction: the candidate asked to stop or said this role is not a fit. "
                "Do not continue the normal interview. If you have not asked for final words yet, ask one brief "
                "final-word question for HR. If final words were already given, close kindly and stop."
            )

        if self.candidate_turns >= 2 and self.low_fit_signals >= 2:
            return (
                "Hard conversation-control instruction: the candidate is answering below the expected bar and "
                "there is enough role-relevant evidence to finish early. Stop probing. Ask for final words for HR, "
                "then close kindly. Do not ask another competency question."
            )

        return ""


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)
