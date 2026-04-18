import io
import logging

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_AI_COMPANY_INFO_FAILED,
    MSG_FILE_EXTRACT_FAILED,
    MSG_INTERNAL_URL_NOT_ALLOWED,
    MSG_INVALID_URL,
    MSG_URL_RESOLVE_FAILED,
    MSG_WEBSITE_EXTRACT_FAILED,
    MSG_WEBSITE_FETCH_FAILED,
)

logger = logging.getLogger(__name__)


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
                    parts=[
                        types.Part(text=f"Generate a company info summary from this {source_label}:\n\n{text[:6000]}")
                    ],
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
        detected_lang = detect_language(description)
        return description, detected_lang
    except Exception as exc:
        logger.exception("Failed to generate company info with AI from %s", source_label)
        raise ApplicationError(str(MSG_AI_COMPANY_INFO_FAILED)) from exc


def detect_language(text: str) -> str:
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
