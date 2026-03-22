import io
import json
import logging

from django.db import models, transaction
from openai import OpenAI

from apps.accounts.models import Company, User
from apps.common.exceptions import ApplicationError
from apps.vacancies.models import InterviewQuestion, ScreeningStep, Vacancy, VacancyCriteria

logger = logging.getLogger(__name__)


DEFAULT_CRITERIA = [
    {"name": "Technical Skills", "description": "Relevant technical knowledge and abilities", "weight": 3, "order": 0},
    {"name": "Communication", "description": "Clarity of expression and listening skills", "weight": 2, "order": 1},
    {"name": "Problem Solving", "description": "Analytical thinking and creative solutions", "weight": 3, "order": 2},
    {"name": "Cultural Fit", "description": "Alignment with company values and team dynamics", "weight": 2, "order": 3},
    {"name": "Experience Relevance", "description": "Relevance of prior experience to the role", "weight": 2, "order": 4},
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
    return vacancy


def update_vacancy(*, vacancy: Vacancy, data: dict) -> Vacancy:
    """Update allowed vacancy fields.

    interview_mode can only be changed if the vacancy has no applications.
    """
    allowed_fields = {
        "title", "description", "requirements", "responsibilities",
        "skills", "salary_min", "salary_max", "salary_currency",
        "location", "is_remote", "employment_type", "experience_level",
        "deadline", "visibility", "interview_duration",
        "interview_mode", "interview_enabled", "cv_required", "company_info",
        "prescanning_prompt", "interview_prompt",
    }

    # Guard: interview_mode cannot be changed once applications exist
    if "interview_mode" in data and data["interview_mode"] != vacancy.interview_mode:
        if vacancy.applications.exists():
            raise ApplicationError(
                "Cannot change interview mode after applications have been submitted."
            )

    update_fields: list[str] = []

    for field, value in data.items():
        if field in allowed_fields:
            setattr(vacancy, field, value)
            update_fields.append(field)

    if not update_fields:
        return vacancy

    update_fields.append("updated_at")
    vacancy.save(update_fields=update_fields)
    return vacancy


def publish_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Publish a vacancy. Allowed from draft or paused.

    Lifecycle: draft → published ↔ paused → archived. Cannot go back to draft.
    """
    if vacancy.status not in (Vacancy.Status.DRAFT, Vacancy.Status.PAUSED):
        raise ApplicationError("Only draft or paused vacancies can be published.")

    if not vacancy.questions.filter(is_active=True, step=ScreeningStep.PRESCANNING).exists():
        raise ApplicationError("Cannot publish a vacancy without active prescanning questions.")

    if vacancy.interview_enabled and not vacancy.questions.filter(is_active=True, step=ScreeningStep.INTERVIEW).exists():
        raise ApplicationError("Cannot publish a vacancy with interview enabled but no active interview questions.")

    vacancy.status = Vacancy.Status.PUBLISHED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def pause_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Pause a published vacancy. Can be resumed (published again)."""
    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError("Only published vacancies can be paused.")

    vacancy.status = Vacancy.Status.PAUSED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def archive_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Archive a vacancy and expire all pending sessions.

    Allowed from published or paused. Terminal state — cannot go back.
    """
    if vacancy.status not in (Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED):
        raise ApplicationError("Only published or paused vacancies can be archived.")

    vacancy.status = Vacancy.Status.ARCHIVED
    vacancy.save(update_fields=["status", "updated_at"])

    # Expire all pending sessions for this vacancy
    from apps.interviews.services import expire_interviews_for_vacancy

    expire_interviews_for_vacancy(vacancy=vacancy)

    return vacancy


def soft_delete_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Soft-delete an archived vacancy. Only archived vacancies can be deleted."""
    if vacancy.status != Vacancy.Status.ARCHIVED:
        raise ApplicationError("Only archived vacancies can be deleted.")
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
    max_order = vacancy.criteria.filter(step=step).aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

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
    max_order = vacancy.questions.filter(step=step).aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

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


def generate_interview_questions(
    *, vacancy: Vacancy, step: str = ScreeningStep.PRESCANNING
) -> list[InterviewQuestion]:
    """Generate questions using OpenAI based on vacancy details and step type."""
    skills_text = ", ".join(vacancy.skills) if vacancy.skills else "not specified"
    criteria = list(vacancy.criteria.filter(step=step).values_list("name", flat=True))
    criteria_text = ", ".join(criteria) if criteria else "general assessment"

    if step == ScreeningStep.PRESCANNING:
        step_instruction = (
            "Generate prescanning questions for a QUICK initial AI screening. "
            "Questions should be lighter — focus on basic fit, motivation, "
            "and general qualifications. Generate 4-7 questions."
        )
    else:
        step_instruction = (
            "Generate interview questions for a RIGOROUS AI interview. "
            "Questions should be tougher — test technical depth, real-world scenarios, "
            "and domain expertise. Generate 7-10 questions."
        )

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert HR interviewer. {step_instruction}\n"
                        "Questions should be:\n"
                        "- Specific to the role and required skills\n"
                        "- A mix of technical, behavioral, and situational questions\n"
                        "- Open-ended (not yes/no)\n"
                        "- Concise (1-2 sentences max)\n\n"
                        "Return JSON with a 'questions' array. Each item has:\n"
                        '- "text": the question\n'
                        '- "category": one of Technical, Behavioral, Situational, Experience, Problem Solving'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Role: {vacancy.title}\n"
                        f"Experience level: {vacancy.experience_level}\n"
                        f"Description: {vacancy.description[:1000]}\n"
                        f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                        f"Skills: {skills_text}\n"
                        f"Evaluation criteria: {criteria_text}"
                    ),
                },
            ],
        )

        data = json.loads(response.choices[0].message.content)
        questions_data = data.get("questions", [])
    except Exception:
        logger.exception("Failed to generate questions with AI for vacancy %s", vacancy.id)
        raise ApplicationError("Failed to generate questions. Please try again.")

    max_order = vacancy.questions.filter(step=step).aggregate(
        max_order=models.Max("order")
    )["max_order"] or 0

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
        raise ApplicationError("Could not extract text from the uploaded file.")

    return _generate_company_info_with_ai(text=text, source_label="document")


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    import PyPDF2

    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
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
        raise ApplicationError("Invalid URL.")

    # Block obvious internal hostnames
    blocked_hostnames = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal"}
    if hostname.lower() in blocked_hostnames:
        raise ApplicationError("Internal URLs are not allowed.")

    try:
        resolved_ip = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)[0][4][0]
        ip = ipaddress.ip_address(resolved_ip)
    except (socket.gaierror, ValueError) as exc:
        raise ApplicationError("Could not resolve the URL hostname.") from exc

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        raise ApplicationError("Internal or private URLs are not allowed.")


def parse_company_info_from_url(*, url: str) -> str:
    """Fetch a webpage and use AI to generate company info from its content."""
    import requests
    from bs4 import BeautifulSoup

    _validate_url_not_internal(url)

    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; HRPreScan/1.0)",
        }, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApplicationError(f"Could not fetch the website: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if not text.strip():
        raise ApplicationError("Could not extract text from the website.")

    return _generate_company_info_with_ai(text=text, source_label="website")


def _generate_company_info_with_ai(*, text: str, source_label: str = "document") -> str:
    """Use AI to generate a company info summary from extracted text."""
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant helping HR managers prepare company descriptions "
                        "for AI-powered candidate interviews. Given the content extracted from a "
                        f"company {source_label}, write a concise "
                        "company introduction (3-5 paragraphs) that an AI interviewer can use to "
                        "introduce the company to candidates.\n\n"
                        "Include: what the company does, industry, mission/values, culture, "
                        "notable achievements or products, and team size if available.\n"
                        "Tone: professional but friendly. Write in third person."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate a company info summary from this {source_label}:\n\n{text[:6000]}",
                },
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("Failed to generate company info with AI from %s", source_label)
        raise ApplicationError(f"Failed to generate company info from {source_label}. Please try again.")
