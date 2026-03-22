from celery import shared_task


@shared_task
def process_telegram_update(update_data):
    """Process a Telegram webhook update asynchronously."""
    from apps.integrations.telegram_bot import handle_update

    handle_update(update_data)
