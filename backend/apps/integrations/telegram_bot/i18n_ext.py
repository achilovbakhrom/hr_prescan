"""Extended bot translations — registration and prescreening flows."""

_STRINGS_EXT: dict[str, dict[str, str]] = {
    # ----- registration -----
    "candidate.reg_ask_name": {
        "en": "👋 Welcome! Let's get you registered.\n\nPlease enter your full name (First Last):",
        "ru": "👋 Добро пожаловать! Давайте зарегистрируем вас.\n\nВведите ваше полное имя (Имя Фамилия):",
        "uz": "👋 Xush kelibsiz! Keling, sizni ro'yxatdan o'tkazamiz.\n\nTo'liq ismingizni kiriting (Ism Familiya):",
    },
    "candidate.reg_ask_phone": {
        "en": "📱 Great, {name}! Now enter your phone number (e.g. +998901234567):",
        "ru": "📱 Отлично, {name}! Теперь введите номер телефона (например +998901234567):",
        "uz": "📱 Ajoyib, {name}! Endi telefon raqamingizni kiriting (masalan +998901234567):",
    },
    "candidate.reg_invalid_name": {
        "en": "Please enter your first and last name (at least two words).",
        "ru": "Пожалуйста, введите имя и фамилию (минимум два слова).",
        "uz": "Iltimos, ism va familiyangizni kiriting (kamida ikki so'z).",
    },
    "candidate.reg_invalid_phone": {
        "en": "Please enter a valid phone number (digits and + only).",
        "ru": "Пожалуйста, введите корректный номер телефона (только цифры и +).",
        "uz": "Iltimos, to'g'ri telefon raqamini kiriting (faqat raqamlar va +).",
    },
    "candidate.reg_complete": {
        "en": (
            "✅ Registration complete!\n\n"
            "Your login details for the web app:\n"
            "📧 Email: `{email}`\n"
            "🔑 Password: `{password}`\n\n"
            "You can also sign in with Telegram on the web."
        ),
        "ru": (
            "✅ Регистрация завершена!\n\n"
            "Ваши данные для входа в веб-приложение:\n"
            "📧 Email: `{email}`\n"
            "🔑 Пароль: `{password}`\n\n"
            "Вы также можете войти через Telegram на сайте."
        ),
        "uz": (
            "✅ Ro'yxatdan o'tish yakunlandi!\n\n"
            "Veb-ilova uchun kirish ma'lumotlaringiz:\n"
            "📧 Email: `{email}`\n"
            "🔑 Parol: `{password}`\n\n"
            "Siz shuningdek veb-saytda Telegram orqali kirishingiz mumkin."
        ),
    },
    # ----- main menu -----
    "candidate.main_menu": {
        "en": "What would you like to do?",
        "ru": "Что хотите сделать?",
        "uz": "Nima qilmoqchisiz?",
    },
    "candidate.btn_prescreening": {
        "en": "🎯 Pass Prescreening",
        "ru": "🎯 Пройти прескрининг",
        "uz": "🎯 Preskreeningdan o'tish",
    },
    # ----- prescreening buttons -----
    "candidate.btn_confirm": {
        "en": "✅ Confirm",
        "ru": "✅ Подтвердить",
        "uz": "✅ Tasdiqlash",
    },
    "candidate.btn_change": {
        "en": "✏️ Change",
        "ru": "✏️ Изменить",
        "uz": "✏️ O'zgartirish",
    },
    "candidate.btn_skip_cv": {
        "en": "Skip (no CV)",
        "ru": "Пропустить (без резюме)",
        "uz": "O'tkazib yuborish (rezyumesiz)",
    },
    # ----- prescreening flow -----
    "candidate.ps_ask_code": {
        "en": "Enter the 6-digit vacancy code provided by HR:",
        "ru": "Введите 6-значный код вакансии от HR:",
        "uz": "HR tomonidan berilgan 6 xonali vakansiya kodini kiriting:",
    },
    "candidate.ps_code_not_found": {
        "en": "Vacancy with code *{code}* not found. Please check and try again.",
        "ru": "Вакансия с кодом *{code}* не найдена. Проверьте код и попробуйте снова.",
        "uz": "*{code}* kodli vakansiya topilmadi. Kodni tekshirib, qayta urinib ko'ring.",
    },
    "candidate.ps_code_invalid": {
        "en": "Please enter a valid 6-digit code (numbers only).",
        "ru": "Введите корректный 6-значный код (только цифры).",
        "uz": "To'g'ri 6 xonali kodni kiriting (faqat raqamlar).",
    },
    "candidate.ps_confirm_name": {
        "en": "📋 *{title}* at _{company}_\n\nYour name for this application:\n*{name}*\n\nIs this correct?",
        "ru": "📋 *{title}* в _{company}_\n\nВаше имя для этой заявки:\n*{name}*\n\nВсё верно?",
        "uz": "📋 *{title}* — _{company}_\n\nBu ariza uchun ismingiz:\n*{name}*\n\nTo'g'rimi?",
    },
    "candidate.ps_ask_new_name": {
        "en": "Enter your full name:",
        "ru": "Введите ваше полное имя:",
        "uz": "To'liq ismingizni kiriting:",
    },
    "candidate.ps_confirm_phone": {
        "en": "Your phone number:\n*{phone}*\n\nIs this correct?",
        "ru": "Ваш номер телефона:\n*{phone}*\n\nВсё верно?",
        "uz": "Telefon raqamingiz:\n*{phone}*\n\nTo'g'rimi?",
    },
    "candidate.ps_ask_new_phone": {
        "en": "Enter your phone number:",
        "ru": "Введите номер телефона:",
        "uz": "Telefon raqamingizni kiriting:",
    },
    "candidate.ps_cv_required": {
        "en": "📎 This vacancy requires a CV. Please upload it (PDF, DOCX, TXT):",
        "ru": "📎 Для этой вакансии требуется резюме. Загрузите его (PDF, DOCX, TXT):",
        "uz": "📎 Bu vakansiya uchun rezyume talab qilinadi. Yuklab bering (PDF, DOCX, TXT):",
    },
    "candidate.ps_cv_optional": {
        "en": "📎 You can attach your CV to strengthen your application (PDF, DOCX, TXT).\nCV is *not mandatory* for this position.",
        "ru": "📎 Вы можете прикрепить резюме для усиления заявки (PDF, DOCX, TXT).\nРезюме *не обязательно* для этой вакансии.",
        "uz": "📎 Arizangizni kuchaytirish uchun rezyume biriktiring (PDF, DOCX, TXT).\nBu vakansiya uchun rezyume *majburiy emas*.",
    },
    "candidate.ps_starting": {
        "en": "🚀 Starting prescreening for *{title}*.\n\nPlease answer each question thoughtfully. You can reply with text or a voice message.",
        "ru": "🚀 Начинаем прескрининг на вакансию *{title}*.\n\nОтвечайте обдуманно. Можно отвечать текстом или голосовым сообщением.",
        "uz": "🚀 *{title}* vakansiyasi uchun preskreeningni boshlayapmiz.\n\nHar bir savolga o'ylab javob bering. Matn yoki ovozli xabar bilan javob berishingiz mumkin.",
    },
    "candidate.ps_question": {
        "en": "❓ *Question {n} of {total}*\n\n{text}",
        "ru": "❓ *Вопрос {n} из {total}*\n\n{text}",
        "uz": "❓ *Savol {n}/{total}*\n\n{text}",
    },
    "candidate.ps_complete": {
        "en": (
            "✅ *Thank you!* Your answers have been submitted.\n\n"
            "The HR team will review your prescreening results and get back to you."
        ),
        "ru": (
            "✅ *Спасибо!* Ваши ответы отправлены.\n\n"
            "HR-команда рассмотрит результаты прескрининга и свяжется с вами."
        ),
        "uz": (
            "✅ *Rahmat!* Javoblaringiz yuborildi.\n\n"
            "HR jamoasi preskreeninz natijalarini ko'rib chiqib, siz bilan bog'lanadi."
        ),
    },
    "candidate.ps_no_questions": {
        "en": "This vacancy has no prescreening questions yet. Please check back later.",
        "ru": "У этой вакансии пока нет вопросов прескрининга. Попробуйте позже.",
        "uz": "Bu vakansiya uchun hali preskreeninz savollari yo'q. Keyinroq urinib ko'ring.",
    },
}
