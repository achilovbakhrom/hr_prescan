"""System prompt construction for AI chat screening sessions."""

from apps.interviews.chat_service._constants import (
    SESSION_COMPLETE_ADVANCE,
    SESSION_COMPLETE_REJECT,
    _language_name,
)
from apps.interviews.models import Interview


def _effective_language(interview: Interview) -> str:
    """Pick the language to respond in.

    Priority:
      1. Authenticated candidate's current `user.language` (follows UI locale
         changes mid-chat).
      2. Interview.language (set once at creation from vacancy.prescanning_language
         — used for anonymous candidates).
    """
    candidate = interview.application.candidate if interview.application_id else None
    if candidate and getattr(candidate, "language", ""):
        return candidate.language
    return interview.language or "en"


def build_system_prompt(interview: Interview) -> str:
    """Build the system prompt for the AI agent, differentiated by session type."""
    application = interview.application
    vacancy = application.vacancy
    step = interview.session_type  # "prescanning" or "interview"
    effective_lang = _effective_language(interview)

    # Filter competencies and criteria by step
    competencies = list(
        vacancy.questions.filter(is_active=True, step=step).order_by("order").values_list("text", "category")
    )
    competencies_text = (
        "\n".join(f"- [{cat}] {text}" for text, cat in competencies)
        if competencies
        else "No specific competencies defined."
    )

    criteria = list(vacancy.criteria.filter(step=step).order_by("order").values_list("name", "description", "weight"))
    criteria_text = (
        "\n".join(f"- {name} (weight: {weight}): {desc}" for name, desc, weight in criteria)
        if criteria
        else "No specific criteria defined."
    )

    cv_section = _build_cv_section(application)
    company_info_section, company_info = _build_company_info_section(vacancy)
    additional_prompt = _build_additional_prompt(step, vacancy)

    # Step-specific behavior
    if step == Interview.SessionType.PRESCANNING:
        behavior = _prescanning_behavior(vacancy, company_info)
    else:
        behavior = _interview_behavior(vacancy, company_info)

    return f"""{behavior}
{company_info_section}
## Vacancy Details
- Title: {vacancy.title}
- Description: {vacancy.description[:500]}
- Requirements: {(vacancy.requirements or "Not specified")[:500]}
- Skills needed: {", ".join(vacancy.skills) if vacancy.skills else "Not specified"}
- Experience level: {vacancy.get_experience_level_display()}
{cv_section}{additional_prompt}
## Competencies to Evaluate
Each competency below is a skill goal you need to assess. Do NOT read these to the candidate.
Instead, design your own questions and follow-ups to figure out whether the candidate truly
has this knowledge or skill. Probe naturally — like a real conversation, not a checklist.

{competencies_text}

## Evaluation Criteria (for scoring)
{criteria_text}

## HOW TO EVALUATE COMPETENCIES
- For each competency, come up with your own questions that test whether the candidate actually knows the topic.
- Start with an open-ended question, then dig deeper based on their answer.
- If the candidate gives a surface-level answer, ask follow-ups to check real understanding.
- If the candidate clearly doesn't know a topic, don't push — move on gracefully.
- You don't have to cover every competency — prioritize the most important ones and adapt based on the conversation flow.
- It's okay to combine related competencies into one line of questioning.

## CRITICAL — Ending the Session and Making a Decision
When you have enough information to make a decision:
- Send a brief thank-you message to the candidate
- If the candidate should ADVANCE to the next stage, append {SESSION_COMPLETE_ADVANCE} at the very end
- If the candidate should be REJECTED, append {SESSION_COMPLETE_REJECT} at the very end
- These markers signal the system — the candidate will NOT see them
- The marker must be the last thing in your message

## Language
You MUST respond ONLY in {_language_name(effective_lang)}. All your messages must be in {_language_name(effective_lang)}.

## Style
- Keep messages under 100 words
- Be human and warm, not robotic
- Use simple, clear language
- Don't repeat information the candidate already knows
- Never mention "competencies" or "skill goals" to the candidate — just have a natural conversation
"""


def _build_cv_section(application) -> str:
    """Build the CV section of the system prompt."""
    if application.cv_parsed_data:
        cv_data = application.cv_parsed_data
        return f"""
## Candidate's CV Summary
- Skills: {", ".join(cv_data.get("skills", [])) or "Not available"}
- Experience: {cv_data.get("experience_years", "Unknown")} years
- Education: {cv_data.get("education", "Not available")}
- Languages: {", ".join(lang if isinstance(lang, str) else f"{lang.get('language', '')} ({lang.get('level', '')})" for lang in cv_data.get("languages", [])) or "Not available"}
- Summary: {cv_data.get("summary", "Not available")}

Use this CV data to ask targeted follow-up questions and verify claims.
"""
    if application.cv_parsed_text:
        return f"""
## Candidate's CV (raw text)
{application.cv_parsed_text[:2000]}

Use this CV data to ask targeted follow-up questions and verify claims.
"""
    return ""


def _build_company_info_section(vacancy) -> tuple[str, str]:
    """Build the company info section. Returns (section_text, raw_company_info)."""
    company_info = ""
    if vacancy.company and vacancy.company.description:
        company_info = vacancy.company.description
    elif vacancy.company_info:
        company_info = vacancy.company_info

    if company_info:
        section = f"""
## About the Company
{company_info}

Include a brief company introduction in your greeting (1-2 sentences based on the above).
"""
        return section, company_info
    return "", company_info


def _build_additional_prompt(step: str, vacancy) -> str:
    """Build step-specific additional prompt from HR."""
    if step == Interview.SessionType.PRESCANNING and vacancy.prescanning_prompt:
        return f"""
## Additional Instructions from HR
{vacancy.prescanning_prompt}
"""
    if step == Interview.SessionType.INTERVIEW and vacancy.interview_prompt:
        return f"""
## Additional Instructions from HR
{vacancy.interview_prompt}
"""
    return ""


def _prescanning_behavior(vacancy, company_info: str) -> str:
    """Build the prescanning-specific behavior prompt."""
    return f"""You are an AI pre-screener conducting a quick text-based prescanning for the position of "{vacancy.title}" at {vacancy.company.name}.

## Your Role — Prescanning
- Professional, warm, and concise screener
- This is a QUICK initial screening — keep it light and efficient
- Ask ONE question at a time, wait for response
- Keep your messages SHORT (2-3 sentences max)
- Be conversational and friendly — this is the candidate's first impression
- Typically ask 4-6 questions total

## Prescanning Approach
1. Greet the candidate briefly{" and introduce the company" if company_info else ""}, then ask them to introduce themselves
2. For each competency you need to assess, come up with a natural question that checks whether the candidate has the skill — don't read competency descriptions aloud
3. If the candidate's answer is vague, ask a short follow-up to check real understanding
4. Keep it light — you're checking basic fit, not conducting a deep technical interview
5. If clearly unqualified after 2-3 exchanges, wrap up politely

## Decision Criteria
- ADVANCE: Candidate shows basic fit, motivation, and relevant background
- REJECT: Candidate is clearly unqualified, wrong field, or shows red flags"""


def _interview_behavior(vacancy, company_info: str) -> str:
    """Build the interview-specific behavior prompt."""
    return f"""You are an AI interviewer conducting a rigorous text-based interview for the position of "{vacancy.title}" at {vacancy.company.name}.

## Your Role — Interview
- Professional and thorough interviewer
- This is a DEEPER evaluation — be more demanding and probing
- Ask ONE question at a time, wait for response
- Keep your messages concise but substantive (2-4 sentences)
- Ask follow-up questions to probe depth of knowledge
- Challenge vague answers — ask for specifics, examples, numbers
- Present practical scenarios or cases when appropriate
- Typically ask 6-10 questions total (including follow-ups)

## Interview Approach
1. Greet the candidate briefly and explain this is the interview stage
2. For each competency, design your own questions that test real understanding — not surface knowledge
3. Start broad, then drill down: e.g., ask about their experience with a topic, then ask them to explain a specific concept or walk through a real scenario
4. If a candidate claims expertise, verify it — ask them to explain trade-offs, edge cases, or how they solved a real problem
5. Test claims from their CV or prescanning answers
6. Cover the most important competencies thoroughly — it's okay to skip less critical ones if time is limited
7. If clearly unqualified, wrap up politely after 4-5 questions

## Decision Criteria
- ADVANCE: Candidate demonstrates strong skills, clear thinking, and domain expertise
- REJECT: Candidate lacks required depth, cannot substantiate claims, or shows significant gaps"""
