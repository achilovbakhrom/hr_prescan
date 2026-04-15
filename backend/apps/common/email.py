"""
Shared email utilities for HR PreScan.

Provides a simple wrapper around Django's send_mail that renders
HTML templates with a consistent branded layout.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_templated_email(
    *,
    to: str | list[str],
    subject: str,
    template: str,
    context: dict | None = None,
) -> bool:
    """Send an HTML email using a template.

    Args:
        to: recipient email(s)
        subject: email subject line
        template: template name under templates/emails/ (e.g. 'verification')
        context: template context variables

    Returns:
        True if sent successfully, False otherwise.
    """
    if isinstance(to, str):
        to = [to]

    ctx = {
        "frontend_url": settings.FRONTEND_URL,
        "app_name": "PreScreen AI",
        **(context or {}),
    }

    html_body = render_to_string(f"emails/{template}.html", ctx)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send()
        logger.info("Email sent: subject=%r, to=%s", subject, to)
        return True
    except Exception:
        logger.exception("Failed to send email: subject=%r, to=%s", subject, to)
        return False
