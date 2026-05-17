"""HR Telegram bot translations."""

from __future__ import annotations

from apps.accounts.models import User
from apps.integrations.telegram_bot.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


def user_lang(user: User | None = None, *, fallback: str = DEFAULT_LANGUAGE) -> str:
    lang = getattr(user, "language", "") or fallback
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def text(key: str, *, user: User | None = None, lang: str = DEFAULT_LANGUAGE, **fmt) -> str:
    messages = _MESSAGES.get(user_lang(user, fallback=lang), _MESSAGES[DEFAULT_LANGUAGE])
    value = messages.get(key) or _MESSAGES[DEFAULT_LANGUAGE].get(key) or key
    return value.format(**fmt) if fmt else value


_MESSAGES = {
    User.Language.EN: {
        "btn_connect": "✅ Connect",
        "btn_cancel": "Cancel",
        "link_confirm": "Connect this Telegram account to {email}?",
        "link_invalid": "This link has expired or is invalid.\n\nPlease generate a new one from Settings -> Telegram.",
        "link_cancelled": "Telegram connection was cancelled.",
        "link_conflict": "This Telegram account is already linked to another user. Please unlink it first.",
        "telegram_invalid": "Invalid Telegram account.",
        "connected": "Connected as {email}{company}\n\nYou can now manage your HR tasks here. Type /help to see what I can do.",
        "welcome_back": "Welcome back, {name}!\n\nType your request or /help to see what I can do.",
        "menu": "Choose what you want to do, or type your request in plain language.",
        "btn_dashboard": "Dashboard",
        "btn_vacancies": "Vacancies",
        "btn_create_vacancy": "Create vacancy",
        "btn_candidates": "Candidates",
        "btn_interviews": "Interviews",
        "btn_team": "Team",
        "btn_subscription": "Subscription",
        "btn_language": "Language",
        "menu_prompt_dashboard": "Show my hiring dashboard and key metrics.",
        "menu_prompt_vacancies": "Show my vacancies with statuses and candidate counts.",
        "menu_prompt_create_vacancy": "Help me create a new vacancy step by step.",
        "menu_prompt_candidates": "Show my recent candidates and their screening statuses.",
        "menu_prompt_interviews": "Show upcoming and recent interviews.",
        "menu_prompt_team": "Show my HR team and available team actions.",
        "menu_prompt_subscription": "Show subscription plan, limits, and current usage.",
        "voice_error": "Sorry, I couldn't transcribe that voice message.",
        "workspace_created": "I created a Telegram workspace for you.\n\nChoose your language to continue.",
        "email_code_sent": "I sent a 6-digit code to {email}.\n\nReply here with that code to connect your Telegram account.",
        "email_link_failed_suffix": "\n\nYou can still create your company directly in Telegram. For example: `Create company Acme in Uzbekistan`.",
        "help": (
            "I can help with:\n\n"
            "*Vacancies* -- list, create, update, publish, pause, archive, delete\n"
            "*Companies* -- list, create, update, delete\n"
            "*Candidates* -- list, status changes, notes\n"
            "*Interviews* -- list, cancel, reset\n"
            "*Dashboard* -- stats, summaries\n"
            "*Subscription* -- plan info, usage\n"
            "*Team* -- invite, manage members\n\n"
            "Just describe what you need in natural language!\n"
            "You can also send voice messages."
        ),
    },
    User.Language.RU: {
        "btn_connect": "✅ Подключить",
        "btn_cancel": "Отмена",
        "link_confirm": "Подключить этот Telegram-аккаунт к {email}?",
        "link_invalid": "Эта ссылка недействительна или устарела.\n\nСоздайте новую в Settings -> Telegram.",
        "link_cancelled": "Подключение Telegram отменено.",
        "link_conflict": "Этот Telegram-аккаунт уже подключён к другому пользователю. Сначала отключите его.",
        "telegram_invalid": "Некорректный Telegram-аккаунт.",
        "connected": "Подключено как {email}{company}\n\nТеперь здесь можно управлять HR-задачами. Напишите /help, чтобы увидеть возможности.",
        "welcome_back": "С возвращением, {name}!\n\nНапишите запрос или /help, чтобы увидеть возможности.",
        "menu": "Выберите действие или напишите задачу обычным текстом.",
        "btn_dashboard": "Дашборд",
        "btn_vacancies": "Вакансии",
        "btn_create_vacancy": "Создать вакансию",
        "btn_candidates": "Кандидаты",
        "btn_interviews": "Интервью",
        "btn_team": "Команда",
        "btn_subscription": "Подписка",
        "btn_language": "Язык",
        "menu_prompt_dashboard": "Покажи дашборд найма и ключевые метрики.",
        "menu_prompt_vacancies": "Покажи мои вакансии со статусами и количеством кандидатов.",
        "menu_prompt_create_vacancy": "Помоги пошагово создать новую вакансию.",
        "menu_prompt_candidates": "Покажи последних кандидатов и их статусы скрининга.",
        "menu_prompt_interviews": "Покажи предстоящие и недавние интервью.",
        "menu_prompt_team": "Покажи мою HR-команду и доступные действия.",
        "menu_prompt_subscription": "Покажи тариф, лимиты и текущее использование.",
        "voice_error": "Извините, я не смог распознать это голосовое сообщение.",
        "workspace_created": "Я создал для вас Telegram-рабочее пространство.\n\nВыберите язык, чтобы продолжить.",
        "email_code_sent": "Я отправил 6-значный код на {email}.\n\nОтветьте этим кодом здесь, чтобы подключить Telegram-аккаунт.",
        "email_link_failed_suffix": "\n\nВы всё равно можете создать компанию прямо в Telegram. Например: `Создай компанию Acme в Узбекистане`.",
        "help": (
            "Я могу помочь с:\n\n"
            "*Вакансиями* -- список, создание, обновление, публикация, пауза, архив, удаление\n"
            "*Компаниями* -- список, создание, обновление, удаление\n"
            "*Кандидатами* -- список, смена статуса, заметки\n"
            "*Интервью* -- список, отмена, сброс\n"
            "*Дашбордом* -- статистика и сводки\n"
            "*Подпиской* -- план и лимиты\n"
            "*Командой* -- приглашения и управление участниками\n\n"
            "Просто опишите задачу обычным языком.\n"
            "Можно также отправлять голосовые сообщения."
        ),
    },
    User.Language.UZ: {
        "btn_connect": "✅ Ulanish",
        "btn_cancel": "Bekor qilish",
        "link_confirm": "Ushbu Telegram akkauntini {email} profiliga ulaysizmi?",
        "link_invalid": "Bu havola noto'g'ri yoki muddati tugagan.\n\nSettings -> Telegram orqali yangi havola yarating.",
        "link_cancelled": "Telegram ulanishi bekor qilindi.",
        "link_conflict": "Bu Telegram akkaunti boshqa foydalanuvchiga ulangan. Avval uni uzing.",
        "telegram_invalid": "Telegram akkaunti noto'g'ri.",
        "connected": "{email}{company} sifatida ulandi\n\nEndi HR vazifalarni shu yerda boshqarishingiz mumkin. Imkoniyatlarni ko'rish uchun /help yuboring.",
        "welcome_back": "Qaytganingiz bilan, {name}!\n\nSo'rovingizni yozing yoki imkoniyatlarni ko'rish uchun /help yuboring.",
        "menu": "Kerakli amalni tanlang yoki vazifani oddiy matnda yozing.",
        "btn_dashboard": "Dashboard",
        "btn_vacancies": "Vakansiyalar",
        "btn_create_vacancy": "Vakansiya yaratish",
        "btn_candidates": "Nomzodlar",
        "btn_interviews": "Suhbatlar",
        "btn_team": "Jamoa",
        "btn_subscription": "Obuna",
        "btn_language": "Til",
        "menu_prompt_dashboard": "Ishga olish dashboardi va asosiy metrikalarni ko'rsat.",
        "menu_prompt_vacancies": "Vakansiyalarimni statuslar va nomzodlar soni bilan ko'rsat.",
        "menu_prompt_create_vacancy": "Yangi vakansiyani bosqichma-bosqich yaratishga yordam ber.",
        "menu_prompt_candidates": "So'nggi nomzodlar va ularning skrining statuslarini ko'rsat.",
        "menu_prompt_interviews": "Yaqinlashayotgan va so'nggi suhbatlarni ko'rsat.",
        "menu_prompt_team": "HR jamoam va mavjud amallarni ko'rsat.",
        "menu_prompt_subscription": "Tarif, limitlar va joriy foydalanishni ko'rsat.",
        "voice_error": "Kechirasiz, bu ovozli xabarni tanib bo'lmadi.",
        "workspace_created": "Siz uchun Telegram ish maydoni yaratdim.\n\nDavom etish uchun tilni tanlang.",
        "email_code_sent": "{email} manziliga 6 xonali kod yubordim.\n\nTelegram akkauntini ulash uchun shu yerda kodni yuboring.",
        "email_link_failed_suffix": "\n\nKompaniyani bevosita Telegramda ham yaratishingiz mumkin. Masalan: `Acme kompaniyasini yarat`.",
        "help": (
            "Men quyidagilarda yordam bera olaman:\n\n"
            "*Vakansiyalar* -- ro'yxat, yaratish, yangilash, e'lon qilish, pauza, arxiv, o'chirish\n"
            "*Kompaniyalar* -- ro'yxat, yaratish, yangilash, o'chirish\n"
            "*Nomzodlar* -- ro'yxat, status o'zgartirish, izohlar\n"
            "*Suhbatlar* -- ro'yxat, bekor qilish, qayta boshlash\n"
            "*Dashboard* -- statistika va xulosalar\n"
            "*Obuna* -- tarif va limitlar\n"
            "*Jamoa* -- taklif va boshqaruv\n\n"
            "Kerakli vazifani oddiy tilda yozing.\n"
            "Ovozli xabar ham yuborishingiz mumkin."
        ),
    },
}
