import logging

import requests
from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


def send_message(*, chat_id, text, parse_mode="Markdown"):
    """Send a message to a Telegram chat."""
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        },
    )


def handle_update(update_data):
    """Process an incoming Telegram update."""
    message = update_data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    telegram_id = message.get("from", {}).get("id")
    telegram_username = message.get("from", {}).get("username", "")

    # Check if voice message
    voice = message.get("voice")
    if voice:
        text = _transcribe_voice(voice.get("file_id"))
        if not text:
            send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't transcribe that voice message.",
            )
            return
        send_message(chat_id=chat_id, text=f"__{text}__", parse_mode="Markdown")
    else:
        text = message.get("text", "").strip()

    if not text:
        return

    # Handle /start command (with optional deep-link payload)
    if text == "/start" or text.startswith("/start "):
        payload = text[7:].strip() if text.startswith("/start ") else ""
        _handle_start(
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            payload=payload,
        )
        return

    # Handle /help command
    if text == "/help":
        _handle_help(chat_id=chat_id, telegram_id=telegram_id)
        return

    # Look up user by telegram_id
    from apps.accounts.models import User

    user = User.objects.filter(telegram_id=telegram_id).first()

    if user is None:
        # Not linked — check if this is a link code
        _try_link_code(
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            text=text,
        )
        return

    # Process AI command
    from apps.common.ai_assistant import process_ai_command

    # Get conversation history from Redis (last 10 messages)
    context = _get_telegram_context(telegram_id=telegram_id, text=text)

    result = process_ai_command(user=user, message=text, context=context)

    response_text = result.get("message", "Something went wrong.")

    # Store in conversation history
    _save_telegram_history(
        telegram_id=telegram_id, user_msg=text, bot_msg=response_text
    )

    send_message(chat_id=chat_id, text=response_text, parse_mode="Markdown")


def _handle_start(*, chat_id, telegram_id, telegram_username="", payload=""):
    """Handle the /start command, optionally auto-linking via deep-link payload."""
    from apps.accounts.models import User

    user = User.objects.filter(telegram_id=telegram_id).first()
    if user:
        send_message(
            chat_id=chat_id,
            text=(
                f"Welcome back, {user.first_name}!\n\n"
                "Type your request or /help to see what I can do."
            ),
        )
        return

    # If a deep-link payload is present, try to auto-link
    if payload:
        _try_deep_link(
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            token=payload,
        )
        return

    send_message(
        chat_id=chat_id,
        text=(
            "Welcome to PreScreen AI!\n\n"
            "To connect your account, go to Settings -> Telegram in the web app "
            "and click the Connect button.\n\n"
            "Don't have an account? Visit https://prescreenai.com to get started."
        ),
    )


def _handle_help(*, chat_id, telegram_id):
    """Handle the /help command."""
    send_message(
        chat_id=chat_id,
        text=(
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
    )


def _try_deep_link(*, chat_id, telegram_id, telegram_username, token):
    """Auto-link account using a deep-link token from /start payload."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone

    from apps.integrations.models import TelegramLinkCode

    try:
        with transaction.atomic():
            link = (
                TelegramLinkCode.objects.filter(
                    code=token, is_used=False, expires_at__gt=timezone.now()
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None:
                send_message(
                    chat_id=chat_id,
                    text=(
                        "This link has expired or is invalid.\n\n"
                        "Please generate a new one from Settings -> Telegram."
                    ),
                )
                return

            if not isinstance(telegram_id, int) or telegram_id <= 0:
                send_message(chat_id=chat_id, text="Invalid Telegram account.")
                return

            user = link.user
            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])

            link.is_used = True
            link.save(update_fields=["is_used", "updated_at"])
    except IntegrityError:
        send_message(
            chat_id=chat_id,
            text="This Telegram account is already linked to another user. Please unlink it first.",
        )
        return

    company_name = user.company.name if user.company else ""
    send_message(
        chat_id=chat_id,
        text=(
            f"Connected as {user.email}"
            + (f" ({company_name})" if company_name else "")
            + "\n\nYou can now manage your HR tasks here. Type /help to see what I can do."
        ),
    )


def _try_link_code(*, chat_id, telegram_id, telegram_username, text):
    """Handle messages from unlinked users."""
    send_message(
        chat_id=chat_id,
        text=(
            "Your Telegram account is not linked yet.\n\n"
            "To connect, go to Settings -> Telegram in the web app "
            "and click the Connect button."
        ),
    )


def _transcribe_voice(file_id):
    """Download Telegram voice message and transcribe with Gemini."""
    if not file_id:
        return None

    try:
        # Get file path from Telegram
        resp = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id})
        file_path = resp.json().get("result", {}).get("file_path")
        if not file_path:
            return None

        # Download the file
        file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
        audio_resp = requests.get(file_url)
        audio_bytes = audio_resp.content

        # Transcribe with Gemini
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg"),
                "Transcribe this audio accurately. The speaker may use Russian, English, "
                "or a mix. Return only the transcription text, nothing else.",
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            ),
        )
        return response.text.strip()
    except Exception as e:
        logger.error("Telegram voice transcription error: %s", e)
        return None


def _get_telegram_context(*, telegram_id, text):
    """Get conversation history from Redis for multi-turn context."""
    from django.core.cache import cache

    key = f"tg_history:{telegram_id}"
    history = cache.get(key, [])
    context = {}
    if history:
        context["conversationHistory"] = history[-10:]
    return context


def _save_telegram_history(*, telegram_id, user_msg, bot_msg):
    """Save conversation to Redis cache (last 20 messages)."""
    from django.core.cache import cache

    key = f"tg_history:{telegram_id}"
    history = cache.get(key, [])
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_msg})
    history = history[-20:]  # Keep last 20 (10 turns)
    cache.set(key, history, timeout=3600 * 24)  # 24 hour TTL
