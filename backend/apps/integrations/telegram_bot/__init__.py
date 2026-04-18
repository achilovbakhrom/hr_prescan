"""Telegram bot package — hosts both HR and candidate bots.

For routing an update to the right bot, use::

    from apps.integrations.telegram_bot.bots import dispatch_update
    dispatch_update(role="hr", update_data=...)

The legacy ``handle_update`` re-export is kept (mapped to the HR bot) so any
existing imports outside this package keep working.
"""

from apps.integrations.telegram_bot.bots import (
    ROLE_CANDIDATE,
    ROLE_HR,
    VALID_ROLES,
    BotConfig,
    dispatch_update,
    get_bot_config,
    get_client,
)

__all__ = [
    "ROLE_CANDIDATE",
    "ROLE_HR",
    "VALID_ROLES",
    "BotConfig",
    "dispatch_update",
    "get_bot_config",
    "get_client",
]
