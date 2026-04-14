from celery import shared_task


@shared_task
def check_expired_trials() -> int:
    """Periodic task: downgrade companies whose free trial has expired."""
    from apps.subscriptions.services import check_and_expire_trials

    return check_and_expire_trials()
