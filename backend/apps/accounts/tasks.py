import logging
from urllib.parse import urljoin

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id: str) -> None:
    """Send email verification link to the user."""
    from apps.accounts.models import User
    from apps.accounts.services import generate_email_verification_token

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning("send_verification_email: user_id=%s not found", user_id)
        return

    token = generate_email_verification_token(user_id=user_id)
    base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    verify_url = f"{base_url}/verify-email?token={token}"

    subject = "Verify your email for HR PreScan"
    text_body = (
        f"Hi {user.first_name or 'there'},\n\n"
        f"Thanks for signing up. Please verify your email by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"If you didn't create an account, you can ignore this message."
    )
    html_body = (
        f"<p>Hi {user.first_name or 'there'},</p>"
        f"<p>Thanks for signing up. Please verify your email by clicking the button below:</p>"
        f'<p><a href="{verify_url}" '
        f'style="display:inline-block;padding:10px 18px;background:#2563eb;color:#fff;'
        f'text-decoration:none;border-radius:6px;">Verify email</a></p>'
        f'<p>Or paste this URL in your browser:<br><a href="{verify_url}">{verify_url}</a></p>'
        f"<p style='color:#666;font-size:12px'>If you didn't create an account, you can ignore this message.</p>"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
        logger.info("Verification email sent to %s (user_id=%s)", user.email, user_id)
    except Exception:
        logger.exception("Failed to send verification email to %s", user.email)
        raise


@shared_task
def send_invitation_email(invitation_id: str) -> None:
    """Send HR invitation email with signup link."""
    from apps.accounts.models import Invitation

    try:
        invitation = Invitation.objects.select_related("company").get(id=invitation_id)
    except Invitation.DoesNotExist:
        logger.warning("send_invitation_email: invitation_id=%s not found", invitation_id)
        return

    base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    accept_url = urljoin(base_url + "/", f"accept-invitation?token={invitation.token}")

    subject = f"You're invited to join {invitation.company.name} on HR PreScan"
    text_body = (
        f"You've been invited to join {invitation.company.name} as an HR manager.\n\n"
        f"Click the link below to accept the invitation:\n{accept_url}\n\n"
        f"This invitation expires in 7 days."
    )
    html_body = (
        f"<p>You've been invited to join <strong>{invitation.company.name}</strong> "
        f"as an HR manager on HR PreScan.</p>"
        f'<p><a href="{accept_url}" '
        f'style="display:inline-block;padding:10px 18px;background:#2563eb;color:#fff;'
        f'text-decoration:none;border-radius:6px;">Accept invitation</a></p>'
        f'<p>Or paste this URL in your browser:<br><a href="{accept_url}">{accept_url}</a></p>'
        f"<p style='color:#666;font-size:12px'>This invitation expires in 7 days.</p>"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invitation.email],
    )
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
        logger.info("Invitation email sent to %s (invitation_id=%s)", invitation.email, invitation_id)
    except Exception:
        logger.exception("Failed to send invitation email to %s", invitation.email)
        raise
