import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Register a webhook URL with the Telegram Bot API."

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="Public HTTPS URL for the webhook (e.g. https://example.com/api/telegram/webhook/)",
        )

    def handle(self, *args, **options):
        url = options["url"]
        token = settings.TELEGRAM_BOT_TOKEN
        secret = settings.TELEGRAM_WEBHOOK_SECRET

        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN is not set in settings.")

        payload = {"url": url}
        if secret:
            payload["secret_token"] = secret

        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        response = requests.post(api_url, json=payload)
        data = response.json()

        if data.get("ok"):
            self.stdout.write(self.style.SUCCESS(f"Webhook set successfully: {url}"))
            self.stdout.write(f"Description: {data.get('description', '')}")
        else:
            raise CommandError(
                f"Failed to set webhook: {data.get('description', 'Unknown error')}"
            )
