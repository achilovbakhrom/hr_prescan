"""Deterministic conversation controls for the voice interviewer."""

from __future__ import annotations

import re


STOP_PATTERNS = (
    r"\b(stop|finish|end|cancel|quit)\s*(the\s+)?(interview|process|call|session)?\b",
    r"\b(enough|that'?s\s+all|no\s+more\s+questions)\b",
    r"\b(can|could|should)\s+(we\s+)?(finish|stop|end)\b",
    r"\b(let'?s|lets)\s+(finish|stop|end)\b",
    r"\bplease\s+(stop|finish|end|cancel)\b",
    r"\b(i\s+)?don'?t\s+want\s+to\s+(continue|pass|do)\b",
    r"\bnot\s+(a\s+)?(fit|match|for\s+me)\b",
    r"\bwrong\s+(role|profession|job|vacancy)\b",
    r"\bnot\s+(a\s+)?(cs\s*go|counter[- ]?strike).{0,24}(player|gamer)\b",
    r"\b(i\s+)?(am|m)\s+not\s+(a\s+)?(cs\s*go|counter[- ]?strike).{0,24}(player|gamer)\b",
    r"\bзаконч",
    r"\bостанов",
    r"\bстоп\b",
    r"\bхватит\b",
    r"\bне\s+хочу\s+(продолж|проход)",
    r"\bне\s+(подхожу|подходит|мой|моя)\b",
    r"\bне\s+игрок\b",
    r"\bдругая\s+професс",
    r"\b(to'xta|toxtat|tugat|bas)\b",
    r"\b(bitir|tamam|durdur|yeter)\b",
    r"\b(détente|arrêter|terminer|stopper)\b",
    r"\b(parar|terminar|cancelar|basta)\b",
    r"\b(beenden|stoppen|abbrechen|genug)\b",
    r"\b(тоқта|аяқта|жетеді)\b",
    r"\b(зупинити|закінчити|досить)\b",
    r"(أوقف|توقف|إنهاء|يكفي)",
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
    r"\b(yakuniy|oxirgi)\s+(fikr|so'z)",
    r"\b(hr|rekruter).{0,40}(ayt|qo'sh)",
    r"\b(son|son bir)\s+(söz|yorum)",
    r"\beklemek\s+istedi",
    r"\b(últim|ultimo).{0,20}(palabra|comentario)",
    r"\balgo\s+(más|mas).{0,30}(agregar|añadir|anadir|decir)",
    r"\b(dernier|final).{0,20}(mot|commentaire)",
    r"\bquelque\s+chose\s+à\s+ajouter",
    r"\b(letzte|abschließende).{0,20}(worte|bemerkung|kommentar)",
    r"\bnoch\s+etwas\s+(sagen|hinzufügen)",
    r"\b(соңғы|ақырғы)\s+сөз",
    r"\bқосқыңыз\s+келе",
    r"\bостанн",
    r"\bщо.*(додати|сказати).*(hr|ейчар|рекрутер)",
    r"(كلمة\s+أخيرة|تعليق\s+أخير|تود.*إضافة)",
)

CLOSING_PATTERNS = (
    r"\b(hr|recruiter|team)\s+will\s+(review|contact|follow)",
    r"\b(interview|session)\s+(is\s+)?(complete|completed|finished|over|ended)\b",
    r"\bthank(s| you).{0,80}(interview|time|answers)\b",
    r"\bспасибо.{0,80}(интервью|ответ|время)\b",
    r"\b(hr|эйчар|рекрутер).{0,60}(рассмотр|свяж)",
    r"\brahmat.{0,80}(suhbat|javob|vaqt)\b",
    r"\bteşekkür.{0,80}(mülakat|cevap|zaman)\b",
    r"\bgracias.{0,80}(entrevista|respuesta|tiempo)\b",
    r"\bmerci.{0,80}(entretien|réponse|temps)\b",
    r"\bdanke.{0,80}(interview|antwort|zeit)\b",
    r"\bдякую.{0,80}(співбесід|відповід|час)\b",
    r"(شكرًا|شكرا).{0,80}(المقابلة|إجاباتك|وقتك)",
)


class ConversationControl:
    """Track hard-stop conditions that the LLM prompt alone may ignore."""

    def __init__(self) -> None:
        self.candidate_turns = 0
        self.low_fit_signals = 0
        self.early_finish_requested = False
        self.final_words_requested = False
        self.final_words_answered = False
        self.interview_closed = False

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
        if _matches_any(normalized, CLOSING_PATTERNS):
            self.interview_closed = True

    def should_shutdown_after_interviewer(self) -> bool:
        return self.final_words_answered and self.interview_closed

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
