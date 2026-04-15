import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id: str) -> None:
    """Send email verification link to the user."""
    from apps.accounts.models import User
    from apps.accounts.services import generate_email_verification_token
    from apps.common.email import send_templated_email

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("send_verification_email: user %s not found", user_id)
        return

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning("send_verification_email: user_id=%s not found", user_id)
        return

    token = generate_email_verification_token(user_id=user_id)
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    send_templated_email(
        to=user.email,
        subject="Verify your email - PreScreen AI",
        template="verification",
        context={
            "user_name": user.first_name or user.email,
            "verification_url": verification_url,
        },
    )


@shared_task
def send_invitation_email(invitation_id: str) -> None:
    """Send HR invitation email with signup/login link."""
    from apps.accounts.models import Invitation, User
    from apps.common.email import send_templated_email

    try:
        invitation = Invitation.objects.select_related("company", "invited_by").get(id=invitation_id)
    except Invitation.DoesNotExist:
        logger.error("send_invitation_email: invitation %s not found", invitation_id)
        return

    existing_user = User.objects.filter(email=invitation.email).exists()
    invitation_url = f"{settings.FRONTEND_URL}/accept-invitation?token={invitation.token}"

    send_templated_email(
        to=invitation.email,
        subject=f"You're invited to join {invitation.company.name} - PreScreen AI",
        template="invitation",
        context={
            "company_name": invitation.company.name,
            "invited_by": invitation.invited_by.full_name,
            "invitation_url": invitation_url,
            "expires_at": invitation.expires_at.strftime("%B %d, %Y"),
            "existing_user": existing_user,
        },
    )
