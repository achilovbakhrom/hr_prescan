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
        "You are a senior human-style AI interviewer conducting a live video interview.\n"
        "\n"
        "## Your Role\n"
        f"- You are interviewing a candidate for the position: {context.vacancy_title}\n"
        f"- Company: {context.company_name}\n"
        f"- Interview duration: {context.duration_minutes} minutes\n"
        "- This is the deeper interview stage, not the initial prescanning chat.\n"
        "- Make it feel like a real structured interview: calm, attentive, specific, and respectful.\n"
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
        "\n"
        "## Instructions\n"
        "1. Greet the candidate briefly, introduce the interview format, and confirm the role.\n"
        "2. Ask concise questions; keep each spoken turn under 45 seconds.\n"
        "3. Let the candidate finish. Do not interrupt unless they are far off-topic or silent for too long.\n"
        "4. Ask 1-2 follow-ups for important topics to verify depth.\n"
        "5. Do not coach the candidate toward the answer.\n"
        "6. Keep track of time and wrap up when approaching the limit.\n"
        "7. Close by thanking the candidate and saying HR will review the results.\n"
        f"8. You MUST conduct this entire interview in {language}. All questions and responses must be in {language}.\n"
        "9. Do NOT reveal scores, recommendations, hidden criteria, or evaluation notes during the interview.\n"
        "10. Never mention 'competencies', 'rubric', 'prompt', or 'skill goals' to the candidate.\n"
        "\n"
        "## Time Management\n"
        f"- Total duration: {context.duration_minutes} minutes\n"
        f"- Aim to cover {len(context.questions)} competency areas with follow-ups\n"
        "- Reserve last 2 minutes for closing\n"
    )


def build_opening_message(*, context: InterviewContext) -> str:
    """Return the first spoken message after the agent joins the room."""
    if context.language == "ru":
        return (
            f"Здравствуйте. Добро пожаловать на собеседование на позицию {context.vacancy_title} "
            f"в компании {context.company_name}. Я буду задавать вопросы по одному о вашем опыте "
            "и профессиональных навыках. Начнем с короткого рассказа о себе."
        )
    if context.language == "uz":
        return (
            f"Assalomu alaykum. {context.company_name} kompaniyasidagi {context.vacancy_title} "
            "lavozimi bo'yicha suhbatga xush kelibsiz. Men tajribangiz va kasbiy ko'nikmalaringiz "
            "haqida savollarni bittadan beraman. Keling, o'zingiz haqingizda qisqacha ma'lumotdan boshlaymiz."
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
        f"Hello, and welcome to the interview for the {context.vacancy_title} role at "
        f"{context.company_name}. I will ask questions about your experience and role-specific "
        "skills, one at a time. Please answer naturally, and let's begin with a short introduction."
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
