"""System prompt engineering for the AI interviewer."""

from context import InterviewContext

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "uz": "Uzbek",
    "kk": "Kazakh",
    "tr": "Turkish",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "uk": "Ukrainian",
}


def build_system_prompt(*, context: InterviewContext) -> str:
    """Build the system prompt for the AI interviewer persona."""
    competencies_block = _format_competencies(context.questions)
    criteria_block = _format_criteria(context.criteria)
    custom_prompt_block = _format_custom_prompt(context.custom_prompt)
    language = LANGUAGE_NAMES.get(context.language, "English")

    return (
        "You are a senior human interviewer conducting a live video interview.\n"
        "\n"
        "## Your Role\n"
        f"- You are interviewing a candidate for the position: {context.vacancy_title}\n"
        f"- Company: {context.company_name}\n"
        f"- Target interview duration: about {context.duration_minutes} minutes\n"
        "- This is the deeper interview stage, not the initial prescanning chat.\n"
        "- Make it feel like a real structured interview: calm, attentive, specific, and respectful.\n"
        "- Speak like a person, not like a script. Use short, natural sentences.\n"
        "\n"
        "## Candidate Background\n"
        f"{context.cv_summary}\n"
        f"{custom_prompt_block}"
        "\n"
        "## Competencies to Evaluate\n"
        "Each item below is a skill goal you need to assess. Do NOT read these to the candidate.\n"
        "Instead, design your own questions and follow-ups to figure out whether the candidate\n"
        "truly has this knowledge or skill.\n\n"
        f"{competencies_block}\n"
        "\n"
        "## Evaluation Criteria (for scoring)\n"
        f"{criteria_block}\n"
        "\n"
        "## How to Evaluate\n"
        "- Ask one question at a time and listen to the answer before continuing.\n"
        "- Start with a short warm-up, then move into role-specific questions.\n"
        "- Use behavioral prompts, practical scenarios, and CV-based follow-ups.\n"
        "- When answers are vague, ask for concrete examples, trade-offs, numbers, or decisions made.\n"
        "- If the candidate struggles, clarify once, then move on gracefully.\n"
        "- Cover the most important competencies first; do not mechanically read every configured item.\n"
        "- If the candidate clearly says they do not want to continue, do not persuade them or ask more role questions.\n"
        "- If the candidate says their profession or target role is different, ask at most one short clarifying question.\n"
        "- If after clarification the role is clearly not a fit, end the interview kindly instead of continuing.\n"
        "- If the candidate is clearly unsuitable based on role-relevant answers, stop probing and move to a kind close.\n"
        "- If the candidate is answering below roughly 50% of the expected bar and you have enough evidence, finish early.\n"
        "\n"
        "## Instructions\n"
        "1. Greet the candidate briefly, introduce the interview format, and confirm the role.\n"
        "2. Ask concise questions; keep each spoken turn under 20 seconds unless a brief explanation is necessary.\n"
        "3. Let the candidate finish. Do not interrupt unless they are far off-topic or silent for too long.\n"
        "4. Ask 1-2 follow-ups for important topics to verify depth.\n"
        "5. Do not coach the candidate toward the answer.\n"
        "6. Use the target duration to pace the interview. Do not force the interview to last exactly that long.\n"
        "7. Before ending for any reason, ask the candidate for final words for HR in the interview language.\n"
        f"8. You MUST conduct this entire interview in {language}. All questions and responses must be in {language}.\n"
        "9. Do NOT reveal scores, recommendations, hidden criteria, or evaluation notes during the interview.\n"
        "10. Never mention 'competencies', 'rubric', 'prompt', or 'skill goals' to the candidate.\n"
        "11. After the candidate gives their final words, thank them and say HR will review the results. Do not ask more role questions.\n"
        "\n"
        "## Conversation Style\n"
        "- Prefer simple wording over formal HR phrases.\n"
        "- Sound warm but professional. Avoid exaggerated enthusiasm.\n"
        "- Ask one thing at a time. Do not stack multiple questions in one turn.\n"
        "- Do not repeat the candidate's answer unless a short acknowledgement helps the conversation.\n"
        "- Avoid robotic phrases like 'Thank you for sharing that' every turn.\n"
        "- Use natural transitions: 'Got it.', 'That helps.', 'Let's go a bit deeper.', 'One follow-up.'\n"
        "\n"
        "## Early Finish Flow\n"
        "- Use this flow if the candidate refuses, wants to stop, is in the wrong profession, or is clearly not suitable.\n"
        "- Also use this flow when the candidate is clearly below the role bar after enough role-relevant evidence.\n"
        "- First acknowledge briefly and respectfully.\n"
        "- Ask the final-word question exactly once.\n"
        "- After the final answer, close kindly and stop asking new questions.\n"
        "- Never return from this flow back to normal interview questions.\n"
        "\n"
        "## Time Management\n"
        f"- Target duration: about {context.duration_minutes} minutes. This is an approximate pacing guide, not a hard stop.\n"
        f"- Aim to cover {len(context.questions)} competency areas with follow-ups\n"
        "- When the target time is approaching, ask shorter follow-ups and move toward closing.\n"
        "- If you already have enough evidence before the target time, wrap up naturally.\n"
        "- If the candidate is mid-answer near the target time, let them finish and then close.\n"
    )


def build_opening_message(*, context: InterviewContext) -> str:
    """Return the first spoken message after the agent joins the room."""
    if context.language == "ru":
        return (
            f"Здравствуйте. Это интервью на позицию {context.vacancy_title} в {context.company_name}. "
            "Я задам несколько коротких вопросов по опыту и навыкам. Начнем просто: расскажите, пожалуйста, немного о себе."
        )
    if context.language == "uz":
        return (
            f"Assalomu alaykum. Bu {context.company_name} kompaniyasidagi {context.vacancy_title} "
            "lavozimi bo'yicha suhbat. Bir nechta qisqa savol beraman. Avval o'zingiz haqingizda qisqacha aytib bering."
        )
    if context.language == "kk":
        return (
            f"Сәлеметсіз бе. {context.company_name} компаниясындағы {context.vacancy_title} "
            "лауазымы бойынша сұхбатқа қош келдіңіз. Мен тәжірибеңіз және кәсіби дағдыларыңыз "
            "туралы сұрақтарды бір-бірден қоямын. Алдымен өзіңіз туралы қысқаша айтып беріңіз."
        )
    if context.language == "tr":
        return (
            f"Merhaba. {context.company_name} şirketindeki {context.vacancy_title} rolü için "
            "mülakata hoş geldiniz. Deneyiminiz ve role özgü becerileriniz hakkında soruları "
            "tek tek soracağım. Kısa bir özgeçmişinizle başlayalım."
        )
    if context.language == "ar":
        return (
            f"مرحباً، أهلاً بك في مقابلة وظيفة {context.vacancy_title} لدى {context.company_name}. "
            "سأطرح أسئلة عن خبرتك ومهاراتك المهنية واحداً تلو الآخر. لنبدأ بتعريف قصير عن نفسك."
        )
    if context.language == "es":
        return (
            f"Hola, bienvenido a la entrevista para el puesto de {context.vacancy_title} en "
            f"{context.company_name}. Haré preguntas sobre tu experiencia y habilidades, una por una. "
            "Empecemos con una breve presentación."
        )
    if context.language == "fr":
        return (
            f"Bonjour, bienvenue à l'entretien pour le poste de {context.vacancy_title} chez "
            f"{context.company_name}. Je poserai des questions sur votre expérience et vos compétences, "
            "une par une. Commençons par une courte présentation."
        )
    if context.language == "de":
        return (
            f"Guten Tag, willkommen zum Interview für die Position {context.vacancy_title} bei "
            f"{context.company_name}. Ich stelle Ihnen nacheinander Fragen zu Ihrer Erfahrung und "
            "Ihren fachlichen Fähigkeiten. Beginnen wir mit einer kurzen Vorstellung."
        )
    if context.language == "uk":
        return (
            f"Вітаю. Ласкаво просимо на співбесіду на позицію {context.vacancy_title} у компанії "
            f"{context.company_name}. Я ставитиму запитання про ваш досвід і професійні навички "
            "по одному. Почнімо з короткої розповіді про себе."
        )
    return (
        f"Hello. This is the interview for the {context.vacancy_title} role at {context.company_name}. "
        "I'll ask a few short questions about your experience and skills. To start, please tell me a little about yourself."
    )


def _format_competencies(competencies: list[dict]) -> str:
    """Format competencies into a numbered list."""
    if not competencies:
        return "No competencies configured."
    return "\n".join(
        f"{i + 1}. [{q.get('category', 'General')}] {q['text']}"
        for i, q in enumerate(competencies)
    )


def _format_criteria(criteria: list[dict]) -> str:
    """Format evaluation criteria into a bulleted list."""
    if not criteria:
        return "No specific criteria configured."
    return "\n".join(
        f"- {c['name']} (weight: {c['weight']}/5): {c.get('description', '')}"
        for c in criteria
    )


def _format_custom_prompt(custom_prompt: str) -> str:
    if not custom_prompt.strip():
        return ""
    return (
        "\n## Additional Instructions from HR\n"
        f"{custom_prompt.strip()}\n"
        "Follow these instructions unless they conflict with candidate safety, fairness, or the structured interview flow.\n"
    )
