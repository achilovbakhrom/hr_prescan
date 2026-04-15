"""Bot-side translations.

Telegram doesn't give us the user's preferred language directly except via
``message.from.language_code`` (BCP-47, e.g. ``ru``, ``en-US``). We map that
to one of our three supported languages and look up strings here.

Strings are intentionally short and split per scope (candidate / hr / common)
to keep this module under the 200-line file limit.
"""

from __future__ import annotations

from typing import Any

SUPPORTED_LANGUAGES = ("en", "ru", "uz")
DEFAULT_LANGUAGE = "en"


def normalize_language(*, lang_code: str | None) -> str:
    """Map a Telegram language_code (e.g. 'ru-RU') to our supported set."""
    if not lang_code:
        return DEFAULT_LANGUAGE
    base = lang_code.split("-")[0].lower()
    if base in SUPPORTED_LANGUAGES:
        return base
    return DEFAULT_LANGUAGE


_STRINGS: dict[str, dict[str, str]] = {
    # ----- common -----
    "common.unknown_command": {
        "en": "Sorry, I didn't understand that. Use /menu to see what I can do.",
        "ru": "Извините, я не понял. Используйте /menu, чтобы увидеть мои возможности.",
        "uz": "Kechirasiz, tushunmadim. Mening imkoniyatlarimni ko‘rish uchun /menu buyrug‘ini yuboring.",
    },
    "common.error_generic": {
        "en": "Something went wrong. Please try again in a moment.",
        "ru": "Что-то пошло не так. Попробуйте ещё раз через минуту.",
        "uz": "Nimadir noto‘g‘ri ketdi. Bir oz vaqtdan keyin qayta urinib ko‘ring.",
    },
    # ----- candidate bot -----
    "candidate.welcome": {
        "en": (
            "👋 Welcome to PreScreen Jobs!\n\n"
            "I'm your AI assistant. I can help you find vacancies, apply, "
            "and complete the screening interview — all from Telegram.\n\n"
            "Use /menu to get started."
        ),
        "ru": (
            "👋 Добро пожаловать в PreScreen Jobs!\n\n"
            "Я ваш AI-ассистент. Помогу найти вакансии, откликнуться и пройти "
            "скрининг — всё прямо в Telegram.\n\n"
            "Используйте /menu, чтобы начать."
        ),
        "uz": (
            "👋 PreScreen Jobs’ga xush kelibsiz!\n\n"
            "Men sizning AI yordamchingizman. Vakansiyalar topish, ariza yuborish "
            "va skrining suhbatini o‘tishda yordam beraman — barchasi Telegram orqali.\n\n"
            "Boshlash uchun /menu yuboring."
        ),
    },
    "candidate.vacancy_not_found": {
        "en": "Sorry, this vacancy is no longer available.",
        "ru": "К сожалению, эта вакансия больше недоступна.",
        "uz": "Kechirasiz, bu vakansiya endi mavjud emas.",
    },
    "candidate.cv_required_prompt": {
        "en": (
            "📎 This vacancy requires a CV.\n\n"
            "Please send me your CV as a PDF or DOCX document, then tap *Apply* again."
        ),
        "ru": (
            "📎 Для этой вакансии требуется резюме.\n\n"
            "Пожалуйста, отправьте резюме в формате PDF или DOCX, затем снова нажмите *Откликнуться*."
        ),
        "uz": (
            "📎 Ushbu vakansiya uchun rezyume talab qilinadi.\n\n"
            "Iltimos, rezyumeingizni PDF yoki DOCX shaklida yuboring va keyin yana *Ariza yuborish* tugmasini bosing."
        ),
    },
    "candidate.cv_uploaded": {
        "en": "✅ CV received. You can now apply to vacancies.",
        "ru": "✅ Резюме получено. Теперь вы можете откликаться на вакансии.",
        "uz": "✅ Rezyume qabul qilindi. Endi vakansiyalarga ariza yuborishingiz mumkin.",
    },
    "candidate.cv_invalid_format": {
        "en": "Please send a PDF, DOCX or DOC file.",
        "ru": "Пожалуйста, отправьте файл в формате PDF, DOCX или DOC.",
        "uz": "Iltimos, PDF, DOCX yoki DOC formatidagi faylni yuboring.",
    },
    "candidate.application_submitted": {
        "en": (
            "✅ *Application submitted!*\n\n"
            "Your application for *{title}* has been received. "
            "I'll DM you here when the recruiter reviews it or when your "
            "screening interview is ready."
        ),
        "ru": (
            "✅ *Отклик отправлен!*\n\n"
            "Ваш отклик на вакансию *{title}* получен. "
            "Я напишу вам сюда, когда рекрутер посмотрит его или когда "
            "будет готов скрининг-интервью."
        ),
        "uz": (
            "✅ *Ariza yuborildi!*\n\n"
            "*{title}* uchun arizangiz qabul qilindi. "
            "Rekruter ko‘rib chiqqanida yoki skrining suhbati tayyor bo‘lganida "
            "shu yerda xabar beraman."
        ),
    },
    "candidate.already_applied": {
        "en": "You have already applied to this vacancy.",
        "ru": "Вы уже откликнулись на эту вакансию.",
        "uz": "Siz allaqachon ushbu vakansiyaga ariza yuborgansiz.",
    },
    "candidate.button_apply": {
        "en": "✅ Apply",
        "ru": "✅ Откликнуться",
        "uz": "✅ Ariza yuborish",
    },
    "candidate.button_back": {
        "en": "◀ Back",
        "ru": "◀ Назад",
        "uz": "◀ Orqaga",
    },
}


def t(key: str, *, lang: str = DEFAULT_LANGUAGE, **fmt: Any) -> str:
    """Look up a translation by key, formatting any ``{var}`` placeholders."""
    entry = _STRINGS.get(key, {})
    text = entry.get(lang) or entry.get(DEFAULT_LANGUAGE) or key
    if fmt:
        try:
            return text.format(**fmt)
        except KeyError, IndexError:
            return text
    return text
