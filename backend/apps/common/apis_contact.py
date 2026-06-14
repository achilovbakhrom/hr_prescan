"""Public contact-form endpoint — emails the support inbox."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def _contact_email() -> str:
    return getattr(settings, "CONTACT_EMAIL", "mailbak36@gmail.com")


class ContactThrottle(AnonRateThrottle):
    scope = "contact"
    rate = "5/hour"


class ContactApi(APIView):
    """POST /api/public/contact/ — forward a contact message to the support inbox."""

    permission_classes = [AllowAny]
    throttle_classes = [ContactThrottle]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=120)
        email = serializers.EmailField()
        subject = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
        message = serializers.CharField(max_length=5000)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        subject = (data["subject"] or "").strip() or "New contact message"
        body = (
            "New contact form submission\n\n"
            f"Name: {data['name']}\n"
            f"Email: {data['email']}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{data['message']}\n"
        )
        message = EmailMessage(
            subject=f"[Contact] {subject}",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[_contact_email()],
            reply_to=[data["email"]],
        )
        try:
            message.send(fail_silently=False)
        except Exception:
            logger.exception("contact form: failed to send email")
            return Response(
                {"detail": "Could not send your message. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"detail": "Message sent."}, status=status.HTTP_200_OK)
