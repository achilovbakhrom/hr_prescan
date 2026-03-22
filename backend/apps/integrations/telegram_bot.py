import logging

import requests
from django.conf import settings
from openai import OpenAI

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

    # Handle /start command
    if text == "/start":
        _handle_start(chat_id=chat_id, telegram_id=telegram_id)
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


def _handle_start(*, chat_id, telegram_id):
    """Handle the /start command."""
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
    else:
        send_message(
            chat_id=chat_id,
            text=(
                "Welcome to PreScreen AI!\n\n"
                "To connect your account, go to Settings -> Telegram in the web app "
                "and send me the 6-digit link code.\n\n"
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


def _try_link_code(*, chat_id, telegram_id, telegram_username, text):
    """Try to interpret the message as a link code."""
    from django.utils import timezone

    from apps.integrations.models import TelegramLinkCode

    code = text.strip()
    if not code.isdigit() or len(code) != 6:
        send_message(
            chat_id=chat_id,
            text=(
                "Your Telegram account is not linked yet.\n\n"
                "To connect, go to Settings -> Telegram in the web app "
                "and send me the 6-digit code."
            ),
        )
        return

    # Rate limit: max 5 link attempts per telegram_id per 10 minutes
    from django.core.cache import cache

    rate_key = f"tg_link_attempts:{telegram_id}"
    attempts = cache.get(rate_key, 0)
    if attempts >= 5:
        send_message(
            chat_id=chat_id,
            text="Too many attempts. Please wait a few minutes and try again.",
        )
        return
    cache.set(rate_key, attempts + 1, timeout=600)

    from django.db import transaction, IntegrityError

    try:
        with transaction.atomic():
            link = (
                TelegramLinkCode.objects.filter(
                    code=code, is_used=False, expires_at__gt=timezone.now()
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None:
                send_message(
                    chat_id=chat_id,
                    text="Invalid or expired code. Please generate a new one from Settings -> Telegram.",
                )
                return

            # Validate telegram_id
            if not isinstance(telegram_id, int) or telegram_id <= 0:
                send_message(chat_id=chat_id, text="Invalid Telegram account.")
                return

            # Link the account
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


def _transcribe_voice(file_id):
    """Download Telegram voice message and transcribe with Whisper."""
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

        # Transcribe with Whisper
        client = OpenAI()
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("voice.ogg", audio_bytes, "audio/ogg"),
            timeout=30.0,
        )
        return transcript.text.strip()
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
