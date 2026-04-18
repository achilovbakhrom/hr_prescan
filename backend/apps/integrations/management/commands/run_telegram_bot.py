"""
Run a Telegram bot in polling mode (for local development).

Usage:
    python manage.py run_telegram_bot --role hr
    python manage.py run_telegram_bot --role candidate

Defaults to ``--role hr`` for backwards compatibility.
For production, use webhook mode instead (setup_telegram_webhook).
"""

import logging
import time

from django.core.management.base import BaseCommand, CommandError

from apps.integrations.telegram_bot.bots import (
    ROLE_HR,
    VALID_ROLES,
    dispatch_update,
    get_bot_config,
    get_client,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run a Telegram bot in polling mode (local dev only)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--role",
            type=str,
            default=ROLE_HR,
            choices=VALID_ROLES,
            help="Which bot to run: hr or candidate (default: hr)",
        )

    def handle(self, *args, **options):
        role = options["role"]
        config = get_bot_config(role=role)
        if not config.token:
            raise CommandError(
                f"Telegram {role} bot token is not configured. Set TELEGRAM_{role.upper()}_BOT_TOKEN in .env."
            )

        client = get_client(role=role)
        client.delete_webhook()
        self.stdout.write(self.style.SUCCESS(f"Webhook deleted. Starting {role} bot in polling mode..."))

        offset = 0
        while True:
            try:
                data = client.get_updates(offset=offset, timeout=30)
                if not data.get("ok"):
                    logger.error("Telegram getUpdates error: %s", data)
                    time.sleep(5)
                    continue

                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    self.stdout.write(f"[{role}] update {update['update_id']}")
                    try:
                        dispatch_update(role=role, update_data=update)
                    except Exception as exc:
                        logger.error("Error processing update: %s", exc, exc_info=True)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS(f"\n{role} bot stopped."))
                break
