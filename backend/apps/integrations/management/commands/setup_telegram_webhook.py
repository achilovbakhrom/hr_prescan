"""Register a webhook URL with the Telegram Bot API for one of our bots.

Usage:
    python manage.py setup_telegram_webhook https://example.com/api/telegram/hr/webhook/ --role hr
    python manage.py setup_telegram_webhook https://example.com/api/telegram/candidate/webhook/ --role candidate
"""
from django.core.management.base import BaseCommand, CommandError

from apps.integrations.telegram_bot.bots import (
    ROLE_HR,
    VALID_ROLES,
    get_bot_config,
    get_client,
)


class Command(BaseCommand):
    help = "Register a webhook URL with the Telegram Bot API."

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="Public HTTPS URL for the webhook (e.g. https://example.com/api/telegram/hr/webhook/)",
        )
        parser.add_argument(
            "--role",
            type=str,
            default=ROLE_HR,
            choices=VALID_ROLES,
            help="Which bot to register: hr or candidate (default: hr)",
        )

    def handle(self, *args, **options):
        url = options["url"]
        role = options["role"]
        config = get_bot_config(role=role)

        if not config.token:
            raise CommandError(
                f"Telegram {role} bot token is not set. "
                f"Set TELEGRAM_{role.upper()}_BOT_TOKEN in env."
            )

        client = get_client(role=role)
        result = client.set_webhook(url=url, secret_token=config.webhook_secret)
        if result.get("ok"):
            self.stdout.write(self.style.SUCCESS(
                f"{role} webhook set successfully: {url}"
            ))
            self.stdout.write(f"Description: {result.get('description', '')}")
        else:
            raise CommandError(
                f"Failed to set {role} webhook: {result.get('description', 'Unknown error')}"
            )
