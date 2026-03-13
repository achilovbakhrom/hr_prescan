"""System prompt engineering for the AI interviewer."""

from context import InterviewContext


def build_system_prompt(*, context: InterviewContext) -> str:
    """Build the system prompt for the AI interviewer persona."""
    questions_block = _format_questions(context.questions)
    criteria_block = _format_criteria(context.criteria)

    return (
        "You are a professional AI interviewer conducting a pre-screening interview.\n"
        "\n"
        "## Your Role\n"
        f"- You are interviewing a candidate for the position: {context.vacancy_title}\n"
        f"- Company: {context.company_name}\n"
        f"- Interview duration: {context.duration_minutes} minutes\n"
        "\n"
        "## Candidate Background\n"
        f"{context.cv_summary}\n"
        "\n"
        "## Interview Questions\n"
        "Ask these questions in order, with natural follow-ups:\n"
        f"{questions_block}\n"
        "\n"
        "## Evaluation Criteria\n"
        "You will evaluate the candidate on:\n"
        f"{criteria_block}\n"
        "\n"
        "## Instructions\n"
        "1. Start by greeting the candidate and introducing yourself.\n"
        "2. Briefly confirm the candidate's identity and the position they applied for.\n"
        "3. Ask the prepared questions one by one.\n"
        "4. For each question, ask 1-2 follow-up questions based on the response.\n"
        "5. Keep track of time — wrap up when approaching the time limit.\n"
        "6. Thank the candidate and explain next steps.\n"
        "7. Speak naturally and professionally.\n"
        "8. If the candidate speaks in Russian, respond in Russian. "
        "If in English, respond in English.\n"
        "9. Do NOT reveal your evaluation scores or notes during the interview.\n"
        "\n"
        "## Time Management\n"
        f"- Total duration: {context.duration_minutes} minutes\n"
        f"- Aim for {len(context.questions)} questions with follow-ups\n"
        "- Reserve last 2 minutes for closing\n"
    )


def _format_questions(questions: list[dict]) -> str:
    """Format interview questions into a numbered list."""
    if not questions:
        return "No questions configured."
    return "\n".join(
        f"{i + 1}. {q['text']} (Category: {q.get('category', 'General')})"
        for i, q in enumerate(questions)
    )


def _format_criteria(criteria: list[dict]) -> str:
    """Format evaluation criteria into a bulleted list."""
    if not criteria:
        return "No specific criteria configured."
    return "\n".join(
        f"- {c['name']} (weight: {c['weight']}/5): {c.get('description', '')}"
        for c in criteria
    )
