"""
Run Telegram bot in polling mode (for local development).

Usage:
    python manage.py run_telegram_bot

For production, use webhook mode instead (setup_telegram_webhook).
"""
import json
import logging
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Telegram bot in polling mode (local dev only)"

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set in .env"))
            return

        api = f"https://api.telegram.org/bot{token}"

        # Delete any existing webhook so polling works
        requests.post(f"{api}/deleteWebhook")
        self.stdout.write(self.style.SUCCESS("Webhook deleted. Starting polling mode..."))

        offset = 0

        while True:
            try:
                resp = requests.get(
                    f"{api}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                    timeout=35,
                )
                data = resp.json()

                if not data.get("ok"):
                    logger.error("Telegram getUpdates error: %s", data)
                    time.sleep(5)
                    continue

                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    self.stdout.write(f"Processing update {update['update_id']}...")

                    try:
                        from apps.integrations.telegram_bot import handle_update
                        handle_update(update)
                    except Exception as e:
                        logger.error("Error processing update: %s", e, exc_info=True)

            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                self.stderr.write("Connection error. Retrying in 5s...")
                time.sleep(5)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\nBot stopped."))
                break
