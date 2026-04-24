"""HR Telegram onboarding gates: language first, company second."""

from __future__ import annotations

from apps.accounts.models import User
from apps.accounts.services import create_user_company
from apps.integrations.telegram_bot.bots import ROLE_HR
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard
from apps.integrations.telegram_bot.sessions import clear_session_field, get_session, update_session

CB_CREATE_COMPANY = "hr:create_company"
CB_LANG_PREFIX = "hr:lang:"
SESSION_AWAITING_COMPANY = "hr_awaiting_company_name"
SESSION_LANGUAGE_SELECTED = "hr_language_selected"


def send_language_picker(*, client, chat_id: int) -> None:
    client.send_message(
        chat_id=chat_id,
        text="Choose language / Выберите язык / Tilni tanlang:",
        reply_markup=inline_keyboard(
            [
                [
                    button(text="English", callback_data=f"{CB_LANG_PREFIX}{User.Language.EN}"),
                    button(text="Русский", callback_data=f"{CB_LANG_PREFIX}{User.Language.RU}"),
                    button(text="O'zbek", callback_data=f"{CB_LANG_PREFIX}{User.Language.UZ}"),
                ],
            ]
        ),
    )


def handle_onboarding_callback(*, client, chat_id: int, telegram_id: int, data: str) -> bool:
    if data.startswith(CB_LANG_PREFIX):
        _handle_language_callback(client=client, chat_id=chat_id, telegram_id=telegram_id, data=data)
        return True
    if data == CB_CREATE_COMPANY:
        update_session(role=ROLE_HR, telegram_id=telegram_id, state=SESSION_AWAITING_COMPANY)
        user = _get_hr_user(telegram_id=telegram_id)
        send_company_name_prompt(client=client, chat_id=chat_id, user=user)
        return True
    return False


def handle_company_name_reply(*, client, chat_id: int, user: User, text: str) -> bool:
    session = get_session(role=ROLE_HR, telegram_id=user.telegram_id)
    if session.get("state") != SESSION_AWAITING_COMPANY or _has_company(user=user):
        return False

    name = text.strip()
    if not name or name.startswith("/"):
        send_company_name_prompt(client=client, chat_id=chat_id, user=user)
        return True

    company = create_user_company(user=user, name=name, size="small", country="")
    clear_session_field(role=ROLE_HR, telegram_id=user.telegram_id, field="state")
    client.send_message(
        chat_id=chat_id,
        text=_text(user=user, key="company_created", company=company.name),
        parse_mode="Markdown",
    )
    return True


def ensure_onboarding_ready(*, client, chat_id: int, user: User, text: str) -> bool:
    if not _language_selected(user=user):
        send_language_picker(client=client, chat_id=chat_id)
        return False

    if _has_company(user=user) or _looks_like_company_creation(text=text):
        return True

    send_company_required(client=client, chat_id=chat_id, user=user)
    return False


def send_company_required(*, client, chat_id: int, user: User | None = None) -> None:
    client.send_message(
        chat_id=chat_id,
        text=_text(user=user, key="company_required"),
        reply_markup=_create_company_keyboard(user=user),
        parse_mode="Markdown",
    )


def send_company_name_prompt(*, client, chat_id: int, user: User | None = None) -> None:
    client.send_message(
        chat_id=chat_id,
        text=_text(user=user, key="company_name_prompt"),
        parse_mode="Markdown",
    )


def is_onboarding_callback(*, data: str) -> bool:
    return data.startswith(CB_LANG_PREFIX) or data == CB_CREATE_COMPANY


def _handle_language_callback(*, client, chat_id: int, telegram_id: int, data: str) -> None:
    language = data.removeprefix(CB_LANG_PREFIX)
    if language not in {User.Language.EN, User.Language.RU, User.Language.UZ}:
        send_language_picker(client=client, chat_id=chat_id)
        return

    user = _get_hr_user(telegram_id=telegram_id)
    if user is None:
        send_language_picker(client=client, chat_id=chat_id)
        return

    user.language = language
    user.save(update_fields=["language", "updated_at"])
    update_session(role=ROLE_HR, telegram_id=telegram_id, **{SESSION_LANGUAGE_SELECTED: True})

    client.send_message(chat_id=chat_id, text=_text(user=user, key="language_saved"))
    if not _has_company(user=user):
        send_company_required(client=client, chat_id=chat_id, user=user)


def _create_company_keyboard(*, user: User | None = None):
    return inline_keyboard(
        [[button(text=_text(user=user, key="create_company_button"), callback_data=CB_CREATE_COMPANY)]]
    )


def _get_hr_user(*, telegram_id: int) -> User | None:
    return User.objects.filter(telegram_id=telegram_id, role__in=[User.Role.ADMIN, User.Role.HR]).first()


def _has_company(*, user: User) -> bool:
    return user.memberships.filter(company__is_deleted=False).exists()


def _language_selected(*, user: User) -> bool:
    if not user.telegram_id:
        return True
    session = get_session(role=ROLE_HR, telegram_id=user.telegram_id)
    return bool(session.get(SESSION_LANGUAGE_SELECTED)) or user.onboarding_completed


def _looks_like_company_creation(*, text: str) -> bool:
    normalized = " ".join(text.casefold().split())
    company_words = ("company", "компан", "kompani", "firma", "organization", "organisation")
    create_words = ("create", "add", "new", "register", "set up", "setup", "созд", "добав", "yangi", "yarat")
    return any(word in normalized for word in company_words) and any(word in normalized for word in create_words)


def _text(*, user: User | None, key: str, company: str = "") -> str:
    lang = (user.language if user is not None else User.Language.EN) or User.Language.EN
    messages = _MESSAGES.get(lang, _MESSAGES[User.Language.EN])
    return messages[key].format(company=company)


_MESSAGES = {
    User.Language.EN: {
        "language_saved": "Language saved.",
        "create_company_button": "Create company",
        "company_required": (
            "Create your company first before managing vacancies, candidates, or interviews.\n\n"
            "For example: `Create company Acme in Uzbekistan`."
        ),
        "company_name_prompt": "Send the company name.",
        "company_created": "Created company `{company}`. You can now create vacancies and manage HR tasks.",
    },
    User.Language.RU: {
        "language_saved": "Язык сохранён.",
        "create_company_button": "Создать компанию",
        "company_required": (
            "Сначала создайте компанию, чтобы управлять вакансиями, кандидатами и интервью.\n\n"
            "Например: `Создай компанию Acme в Узбекистане`."
        ),
        "company_name_prompt": "Отправьте название компании.",
        "company_created": "Компания `{company}` создана. Теперь можно создавать вакансии и управлять HR-задачами.",
    },
    User.Language.UZ: {
        "language_saved": "Til saqlandi.",
        "create_company_button": "Kompaniya yaratish",
        "company_required": (
            "Vakansiyalar, nomzodlar va suhbatlarni boshqarishdan oldin kompaniya yarating.\n\n"
            "Masalan: `Acme kompaniyasini yarat`."
        ),
        "company_name_prompt": "Kompaniya nomini yuboring.",
        "company_created": (
            "`{company}` kompaniyasi yaratildi. Endi vakansiyalar va HR vazifalarni boshqarishingiz mumkin."
        ),
    },
}
