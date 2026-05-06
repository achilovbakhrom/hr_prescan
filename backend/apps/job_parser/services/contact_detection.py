import re
from collections.abc import Mapping
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
TELEGRAM_RE = re.compile(
    r"(?:https?://)?(?:t\.me|telegram\.me)/[A-Z0-9_]{5,}|(?<![\w.])@[A-Z0-9_]{5,}\b",
    re.IGNORECASE,
)
WHATSAPP_RE = re.compile(r"\b(?:whats?app|wa\.me/\d{7,}|ватсап|вотсап)\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\s().-]*){9,}")
PHONE_CONTEXT_RE = re.compile(r"(?:phone|tel|call|contact|тел|звон|номер|whats?app)", re.IGNORECASE)


def parsed_vacancy_has_contact_info(vacancy: Any) -> bool:
    raw_payload = vacancy.raw_payload if isinstance(vacancy.raw_payload, Mapping) else {}
    if _contacts_payload_has_contact(raw_payload.get("contacts")):
        return True

    text_parts = [
        getattr(vacancy, "description", ""),
        getattr(vacancy, "requirements", ""),
        getattr(vacancy, "responsibilities", ""),
        raw_payload.get("description", ""),
    ]
    return text_has_contact_info(" ".join(str(part or "") for part in text_parts))


def parsed_vacancy_is_publicly_usable(vacancy: Any) -> bool:
    """A parsed vacancy must expose a contact path or a source URL before public display."""
    return bool(str(getattr(vacancy, "external_url", "") or "").strip()) or parsed_vacancy_has_contact_info(vacancy)


def text_has_contact_info(text: str) -> bool:
    if EMAIL_RE.search(text) or TELEGRAM_RE.search(text) or WHATSAPP_RE.search(text):
        return True
    return _text_has_phone(text)


def _contacts_payload_has_contact(contacts: Any) -> bool:
    if not isinstance(contacts, Mapping):
        return False
    if str(contacts.get("email") or "").strip():
        return True
    phones = contacts.get("phones")
    if isinstance(phones, list):
        return any(_phone_payload_has_number(phone) for phone in phones)
    return False


def _phone_payload_has_number(phone: Any) -> bool:
    if not isinstance(phone, Mapping):
        return False
    fields = [phone.get("country"), phone.get("city"), phone.get("number"), phone.get("formatted")]
    return bool("".join(str(value or "") for value in fields).strip())


def _text_has_phone(text: str) -> bool:
    for match in PHONE_RE.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if not 9 <= len(digits) <= 15:
            continue
        context_start = max(0, match.start() - 24)
        context = text[context_start : match.start()]
        if candidate.lstrip().startswith("+") or digits.startswith(("998", "7", "8")):
            return True
        if PHONE_CONTEXT_RE.search(context):
            return True
    return False
