import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id: str) -> None:
    """Send email verification link to the user.

    Stub implementation — logs the action for now.
    """
    from apps.accounts.services import generate_email_verification_token

    token = generate_email_verification_token(user_id=user_id)
    logger.info("Sending verification email to user_id=%s with token=%s", user_id, token)


@shared_task
def send_invitation_email(invitation_id: str) -> None:
    """Send HR invitation email with signup link.

    Stub implementation — logs the action for now.
    """
    logger.info("Sending invitation email for invitation_id=%s", invitation_id)
