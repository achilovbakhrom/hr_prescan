import io
import json
import logging

from django.conf import settings
from django.db import models, transaction
from google import genai
from google.genai import types

from apps.accounts.models import Company, User
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_AI_COMPANY_INFO_FAILED,
    MSG_AI_QUESTIONS_FAILED,
    MSG_CANNOT_CHANGE_MODE,
    MSG_EMPLOYER_HAS_VACANCIES,
    MSG_FILE_EXTRACT_FAILED,
    MSG_INTERNAL_URL_NOT_ALLOWED,
    MSG_INVALID_URL,
    MSG_NO_INTERVIEW_QUESTIONS,
    MSG_NO_PRESCANNING_QUESTIONS,
    MSG_ONLY_DRAFT_PAUSED_PUBLISH,
    MSG_ONLY_PUBLISHED_PAUSE,
    MSG_ONLY_PUBLISHED_PAUSED_ARCHIVE,
    MSG_URL_RESOLVE_FAILED,
    MSG_WEBSITE_EXTRACT_FAILED,
    MSG_WEBSITE_FETCH_FAILED,
)
from apps.vacancies.models import EmployerCompany, InterviewQuestion, ScreeningStep, Vacancy, VacancyCriteria

logger = logging.getLogger(__name__)


DEFAULT_CRITERIA = [
    {"name": "Technical Skills", "description": "Relevant technical knowledge and abilities", "weight": 3, "order": 0},
    {"name": "Communication", "description": "Clarity of expression and listening skills", "weight": 2, "order": 1},
    {"name": "Problem Solving", "description": "Analytical thinking and creative solutions", "weight": 3, "order": 2},
    {"name": "Cultural Fit", "description": "Alignment with company values and team dynamics", "weight": 2, "order": 3},
    {
        "name": "Experience Relevance",
        "description": "Relevance of prior experience to the role",
        "weight": 2,
        "order": 4,
    },
]


@transaction.atomic
def create_vacancy(
    *,
    company: Company,
    created_by: User,
    title: str,
    description: str,
    **kwargs: object,
) -> Vacancy:
    """Create a vacancy with default evaluation criteria."""
    vacancy = Vacancy.objects.create(
        company=company,
        created_by=created_by,
        title=title,
        description=description,
        **kwargs,
    )
    create_default_criteria(vacancy=vacancy)

    from apps.vacancies.tasks import generate_keywords_task

    transaction.on_commit(lambda: generate_keywords_task.delay(str(vacancy.id)))

    return vacancy


def update_vacancy(*, vacancy: Vacancy, data: dict) -> Vacancy:
    """Update allowed vacancy fields.

    interview_mode can only be changed if the vacancy has no applications.
    """
    allowed_fields = {
        "title",
        "description",
        "requirements",
        "responsibilities",
        "skills",
        "salary_min",
        "salary_max",
        "salary_currency",
        "location",
        "is_remote",
        "employment_type",
        "experience_level",
        "deadline",
        "visibility",
        "interview_duration",
        "interview_mode",
        "interview_enabled",
        "cv_required",
        "company_info",
        "prescanning_prompt",
        "interview_prompt",
        "prescanning_language",
    }

    # Guard: interview_mode cannot be changed once applications exist
    if "interview_mode" in data and data["interview_mode"] != vacancy.interview_mode and vacancy.applications.exists():
        raise ApplicationError(str(MSG_CANNOT_CHANGE_MODE))

    update_fields: list[str] = []

    for field, value in data.items():
        if field in allowed_fields:
            setattr(vacancy, field, value)
            update_fields.append(field)

    if not update_fields:
        return vacancy

    update_fields.append("updated_at")
    vacancy.save(update_fields=update_fields)

    # Regenerate keywords when search-relevant fields change
    search_relevant_fields = {"title", "description", "requirements", "skills"}
    if search_relevant_fields & set(update_fields):
        from apps.vacancies.tasks import generate_keywords_task

        transaction.on_commit(lambda: generate_keywords_task.delay(str(vacancy.id)))

    return vacancy


def publish_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Publish a vacancy. Allowed from draft or paused.

    Lifecycle: draft → published ↔ paused → archived. Cannot go back to draft.
    """
    if vacancy.status not in (Vacancy.Status.DRAFT, Vacancy.Status.PAUSED):
        raise ApplicationError(str(MSG_ONLY_DRAFT_PAUSED_PUBLISH))

    if not vacancy.questions.filter(is_active=True, step=ScreeningStep.PRESCANNING).exists():
        raise ApplicationError(str(MSG_NO_PRESCANNING_QUESTIONS))

    if (
        vacancy.interview_enabled
        and not vacancy.questions.filter(is_active=True, step=ScreeningStep.INTERVIEW).exists()
    ):
        raise ApplicationError(str(MSG_NO_INTERVIEW_QUESTIONS))

    vacancy.status = Vacancy.Status.PUBLISHED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def pause_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Pause a published vacancy. Can be resumed (published again)."""
    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError(str(MSG_ONLY_PUBLISHED_PAUSE))

    vacancy.status = Vacancy.Status.PAUSED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def archive_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Archive a vacancy and expire all pending sessions.

    Allowed from published or paused. Terminal state — cannot go back.
    """
    if vacancy.status not in (Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED):
        raise ApplicationError(str(MSG_ONLY_PUBLISHED_PAUSED_ARCHIVE))

    vacancy.status = Vacancy.Status.ARCHIVED
    vacancy.save(update_fields=["status", "updated_at"])

    # Expire all pending sessions for this vacancy
    from apps.interviews.services import expire_interviews_for_vacancy

    expire_interviews_for_vacancy(vacancy=vacancy)

    return vacancy


def soft_delete_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Soft-delete a vacancy. Only draft or archived vacancies can be deleted."""
    if vacancy.status not in (Vacancy.Status.DRAFT, Vacancy.Status.ARCHIVED):
        raise ApplicationError("Only draft or archived vacancies can be deleted.")
    vacancy.is_deleted = True
    vacancy.save(update_fields=["is_deleted", "updated_at"])
    return vacancy


def create_default_criteria(*, vacancy: Vacancy) -> list[VacancyCriteria]:
    """Create the default set of evaluation criteria for prescanning."""
    criteria_list = []
    for item in DEFAULT_CRITERIA:
        criteria = VacancyCriteria.objects.create(
            vacancy=vacancy,
            name=item["name"],
            description=item["description"],
            weight=item["weight"],
            order=item["order"],
            is_default=True,
            step=ScreeningStep.PRESCANNING,
        )
        criteria_list.append(criteria)
    return criteria_list


def add_vacancy_criteria(
    *,
    vacancy: Vacancy,
    name: str,
    description: str = "",
    weight: int = 1,
    step: str = ScreeningStep.PRESCANNING,
) -> VacancyCriteria:
    """Add a custom evaluation criteria to a vacancy."""
    max_order = vacancy.criteria.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    return VacancyCriteria.objects.create(
        vacancy=vacancy,
        name=name,
        description=description,
        weight=weight,
        is_default=False,
        order=max_order + 1,
        step=step,
    )


def update_vacancy_criteria(*, criteria: VacancyCriteria, **kwargs: object) -> VacancyCriteria:
    """Update a vacancy criteria."""
    allowed_fields = {"name", "description", "weight", "order"}
    update_fields: list[str] = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(criteria, field, value)
            update_fields.append(field)

    if not update_fields:
        return criteria

    update_fields.append("updated_at")
    criteria.save(update_fields=update_fields)
    return criteria


def delete_vacancy_criteria(*, criteria: VacancyCriteria) -> None:
    """Delete a vacancy criteria."""
    criteria.delete()


def add_interview_question(
    *,
    vacancy: Vacancy,
    text: str,
    category: str = "",
    source: str = "hr_added",
    step: str = ScreeningStep.PRESCANNING,
) -> InterviewQuestion:
    """Add a question to a vacancy for the specified step."""
    max_order = vacancy.questions.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    return InterviewQuestion.objects.create(
        vacancy=vacancy,
        text=text,
        category=category,
        source=source,
        order=max_order + 1,
        step=step,
    )


def update_interview_question(*, question: InterviewQuestion, **kwargs: object) -> InterviewQuestion:
    """Update an interview question."""
    allowed_fields = {"text", "category", "order", "is_active"}
    update_fields: list[str] = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(question, field, value)
            update_fields.append(field)

    if not update_fields:
        return question

    update_fields.append("updated_at")
    question.save(update_fields=update_fields)
    return question


def delete_interview_question(*, question: InterviewQuestion) -> None:
    """Delete an interview question."""
    question.delete()


def generate_interview_questions(*, vacancy: Vacancy, step: str = ScreeningStep.PRESCANNING) -> list[InterviewQuestion]:
    """Generate questions using Gemini based on vacancy details and step type."""
    skills_text = ", ".join(vacancy.skills) if vacancy.skills else "not specified"
    criteria = list(vacancy.criteria.filter(step=step).values_list("name", flat=True))
    criteria_text = ", ".join(criteria) if criteria else "general assessment"

    if step == ScreeningStep.PRESCANNING:
        step_instruction = (
            "Generate 4-7 competencies for a QUICK initial AI prescanning. "
            "Focus on foundational skills, basic fit, motivation, and general "
            "qualifications the candidate must demonstrate."
        )
    else:
        step_instruction = (
            "Generate 7-10 competencies for a RIGOROUS AI interview. "
            "Focus on deeper technical skills, real-world problem solving, "
            "domain expertise, and advanced knowledge the candidate must demonstrate."
        )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=
                        f"Role: {vacancy.title}\n"
                        f"Experience level: {vacancy.experience_level}\n"
                        f"Description: {vacancy.description[:1000]}\n"
                        f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                        f"Skills: {skills_text}\n"
                        f"Evaluation criteria: {criteria_text}"
                    )],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                system_instruction=(
                    f"You are an expert HR interviewer. {step_instruction}\n\n"
                    "Each competency is a SKILL GOAL — something the AI interviewer "
                    "should evaluate the candidate on. These are NOT literal questions. "
                    "The AI interviewer will decide how to probe each competency through "
                    "its own follow-up questions during the conversation.\n\n"
                    "Write each competency as a clear goal statement. Examples:\n"
                    '- "Candidate should demonstrate proficiency with React hooks (useState, useEffect, custom hooks)"\n'
                    '- "Candidate should show understanding of RESTful API design and best practices"\n'
                    '- "Candidate should be able to explain their approach to handling tight deadlines"\n'
                    '- "Candidate should demonstrate knowledge of financial reporting standards"\n\n'
                    "Make competencies specific to the role, not generic. "
                    "Write in natural, human-like language.\n\n"
                    "Return JSON with a 'competencies' array. Each item has:\n"
                    '- "text": the competency goal (1-2 sentences)\n'
                    '- "category": one of "Hard Skill", "Soft Skill", "Domain Knowledge", "Cultural Fit"'
                ),
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        data = json.loads(response.text)
        questions_data = data.get("competencies", data.get("questions", []))
    except Exception:
        logger.exception("Failed to generate questions with AI for vacancy %s", vacancy.id)
        raise ApplicationError(str(MSG_AI_QUESTIONS_FAILED))

    max_order = vacancy.questions.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    created_questions: list[InterviewQuestion] = []
    for i, q in enumerate(questions_data, start=1):
        question = InterviewQuestion.objects.create(
            vacancy=vacancy,
            text=q.get("text", ""),
            category=q.get("category", "General"),
            source=InterviewQuestion.Source.AI_GENERATED,
            order=max_order + i,
            step=step,
        )
        created_questions.append(question)

    return created_questions


def generate_vacancy_keywords(*, vacancy: Vacancy) -> list[str]:
    """Generate search keywords using AI for a vacancy."""
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=
                    f"Title: {vacancy.title}\n"
                    f"Description: {vacancy.description[:2000]}\n"
                    f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                    f"Skills: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}"
                )],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "Generate 20-30 search keywords for this job vacancy. "
                "Include ALL of these categories:\n"
                "- Job title synonyms and variations\n"
                "- Broad field/industry terms (e.g. 'programming', 'software development', 'IT')\n"
                "- Related roles and specializations\n"
                "- Key skills and technologies mentioned\n"
                "- Industry jargon and abbreviations\n"
                "- Common search terms a job seeker would use\n"
                "Generate keywords in BOTH English and Russian. "
                'Return JSON: {"keywords": ["keyword1", "keyword2", ...]}'
            ),
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    data = json.loads(response.text)
    keywords = data.get("keywords", [])
    vacancy.keywords = keywords
    vacancy.save(update_fields=["keywords", "updated_at"])
    return keywords


def update_vacancy_search_vector(*, vacancy: Vacancy) -> None:
    """Update the pre-computed search vector for a vacancy.

    Uses both 'english' (for stemming: program matches programming) and
    'simple' (for exact matches of non-English words like Russian).
    """
    from django.contrib.postgres.search import SearchVector
    from django.db.models import Value

    skills_text = " ".join(vacancy.skills) if vacancy.skills else ""
    keywords_text = " ".join(vacancy.keywords) if vacancy.keywords else ""

    Vacancy.objects.filter(id=vacancy.id).update(
        search_vector=(
            # English stemming (program → programming, develop → developer)
            SearchVector("title", weight="A", config="english")
            + SearchVector(Value(skills_text), weight="A", config="english")
            + SearchVector(Value(keywords_text), weight="A", config="english")
            + SearchVector("requirements", weight="B", config="english")
            + SearchVector("description", weight="C", config="english")
            # Simple config for exact matches (Russian words, abbreviations)
            + SearchVector("title", weight="A", config="simple")
            + SearchVector(Value(skills_text), weight="A", config="simple")
            + SearchVector(Value(keywords_text), weight="A", config="simple")
        )
    )


def parse_company_info_from_file(*, file_obj) -> str:
    """Extract text from an uploaded file (PDF/DOCX/TXT) and use AI to generate company info."""
    filename = getattr(file_obj, "name", "file.txt")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    file_bytes = file_obj.read()

    if ext == "pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        text = _extract_text_from_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    if not text.strip():
        raise ApplicationError(str(MSG_FILE_EXTRACT_FAILED))

    description, _ = _generate_company_info_with_ai(text=text, source_label="document")
    return description


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    import docx

    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _validate_url_not_internal(url: str) -> None:
    """Reject URLs pointing to private/internal networks to prevent SSRF."""
    import ipaddress
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ApplicationError(str(MSG_INVALID_URL))

    # Block obvious internal hostnames
    blocked_hostnames = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal"}
    if hostname.lower() in blocked_hostnames:
        raise ApplicationError(str(MSG_INTERNAL_URL_NOT_ALLOWED))

    try:
        resolved_ip = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)[0][4][0]
        ip = ipaddress.ip_address(resolved_ip)
    except (socket.gaierror, ValueError) as exc:
        raise ApplicationError(str(MSG_URL_RESOLVE_FAILED)) from exc

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        raise ApplicationError(str(MSG_INTERNAL_URL_NOT_ALLOWED))


def parse_company_info_from_url(*, url: str) -> str:
    """Fetch a webpage and use AI to generate company info from its content."""
    import requests
    from bs4 import BeautifulSoup

    _validate_url_not_internal(url)

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; HRPreScan/1.0)",
            },
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApplicationError(str(MSG_WEBSITE_FETCH_FAILED)) from exc

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if not text.strip():
        raise ApplicationError(str(MSG_WEBSITE_EXTRACT_FAILED))

    description, _ = _generate_company_info_with_ai(text=text, source_label="website")
    return description


def _generate_company_info_with_ai(*, text: str, source_label: str = "document") -> tuple[str, str]:
    """Use AI to generate a company info summary from extracted text.

    Returns (description, detected_language_code).
    """
    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=
                        f"Generate a company info summary from this {source_label}:\n\n{text[:6000]}"
                    )],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                system_instruction=(
                    "You are an AI assistant helping HR managers prepare company descriptions "
                    "for AI-powered candidate interviews. Given the content extracted from a "
                    f"company {source_label}, write a concise "
                    "company introduction (3-5 paragraphs) that an AI interviewer can use to "
                    "introduce the company to candidates.\n\n"
                    "Write in the same language as the source content. "
                    "If the source is in Russian, write in Russian. If in English, write in English. "
                    "If in Uzbek, write in Uzbek.\n\n"
                    "Include: what the company does, industry, mission/values, culture, "
                    "notable achievements or products, and team size if available.\n"
                    "Tone: professional but friendly. Write in third person."
                ),
                temperature=0.3,
            ),
        )
        description = response.text.strip()
        # Simple language detection heuristic
        detected_lang = _detect_language(description)
        return description, detected_lang
    except Exception:
        logger.exception("Failed to generate company info with AI from %s", source_label)
        raise ApplicationError(str(MSG_AI_COMPANY_INFO_FAILED))


def _detect_language(text: str) -> str:
    """Simple heuristic to detect content language from text."""
    if not text:
        return "en"
    # Count Cyrillic characters
    cyrillic_count = sum(1 for c in text[:500] if "\u0400" <= c <= "\u04ff")
    total_alpha = sum(1 for c in text[:500] if c.isalpha())
    if total_alpha > 0 and cyrillic_count / total_alpha > 0.3:
        return "ru"
    # Check for Uzbek-specific characters (o', g', sh, ch patterns are common in Latin Uzbek)
    uz_markers = ["o'", "g'", "sh", "ch", "ng"]
    lower_text = text[:500].lower()
    uz_count = sum(lower_text.count(m) for m in uz_markers)
    if uz_count >= 3:
        return "uz"
    return "en"


# ---------------------------------------------------------------------------
# Employer Company services
# ---------------------------------------------------------------------------


def create_employer(*, company: Company, name: str, **kwargs: object) -> EmployerCompany:
    """Create a manually-entered employer company."""
    return EmployerCompany.objects.create(company=company, name=name, **kwargs)


def create_employer_from_file(*, company: Company, name: str, file_obj: object) -> EmployerCompany:
    """Create an employer company with description parsed from an uploaded file."""
    description = parse_company_info_from_file(file_obj=file_obj)
    detected_lang = _detect_language(description)
    return EmployerCompany.objects.create(
        company=company,
        name=name,
        description=description,
        description_translations={detected_lang: description},
        source=EmployerCompany.Source.FILE,
    )


def create_employer_from_url(*, company: Company, name: str, url: str) -> EmployerCompany:
    """Create an employer company with description parsed from a website URL."""
    description = parse_company_info_from_url(url=url)
    detected_lang = _detect_language(description)
    return EmployerCompany.objects.create(
        company=company,
        name=name,
        description=description,
        description_translations={detected_lang: description},
        source=EmployerCompany.Source.WEBSITE,
    )


def update_employer(*, employer: EmployerCompany, data: dict) -> EmployerCompany:
    """Update allowed employer company fields."""
    allowed_fields = {"name", "industry", "logo", "website", "description"}
    update_fields: list[str] = []
    for field, value in data.items():
        if field in allowed_fields:
            setattr(employer, field, value)
            update_fields.append(field)
    if update_fields:
        update_fields.append("updated_at")
        employer.save(update_fields=update_fields)
    return employer


def delete_employer(*, employer: EmployerCompany) -> None:
    """Delete an employer company. Raises if it has linked vacancies."""
    if employer.vacancies.exists():
        raise ApplicationError(str(MSG_EMPLOYER_HAS_VACANCIES))
    employer.delete()
