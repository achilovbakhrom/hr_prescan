from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class PublicAppConfigApi(APIView):
    """GET /api/public/app-config/ — small public runtime config for the SPA."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "telegram_hr_bot_username": settings.TELEGRAM_HR_BOT_USERNAME.lstrip("@"),
                "telegram_candidate_bot_username": (
                    settings.TELEGRAM_CANDIDATE_BOT_USERNAME or settings.TELEGRAM_HR_BOT_USERNAME
                ).lstrip("@"),
            }
        )
