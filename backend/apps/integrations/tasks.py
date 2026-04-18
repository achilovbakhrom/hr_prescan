from celery import shared_task


@shared_task
def process_telegram_update(update_data, bot_role: str = "hr"):
    """Process a Telegram webhook update asynchronously.

    Args:
        update_data: raw Telegram Update payload
        bot_role: which bot the update came from (``hr`` or ``candidate``)
    """
    from apps.integrations.telegram_bot.bots import dispatch_update

    dispatch_update(role=bot_role, update_data=update_data)
