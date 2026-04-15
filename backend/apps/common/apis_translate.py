import time
from collections import defaultdict

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission
from apps.common.services_translation import TRANSLATABLE_FIELDS, batch_translate_vacancy_items, translate_ai_content

# Simple in-memory rate limiter: max 50 requests per user per hour
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 50
RATE_LIMIT_WINDOW = 3600


def _check_rate_limit(user_id: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    _rate_limit_store[user_id] = [t for t in _rate_limit_store[user_id] if t > window_start]
    if len(_rate_limit_store[user_id]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit_store[user_id].append(now)
    return True


class TranslateInputSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=50)
    object_id = serializers.UUIDField()
    field = serializers.CharField(max_length=50)
    target_language = serializers.ChoiceField(choices=["en", "ru", "uz"])

    def validate(self, attrs):
        key = (attrs["model"], attrs["field"])
        if key not in TRANSLATABLE_FIELDS:
            raise serializers.ValidationError(
                f"Invalid model/field combination: {attrs['model']}/{attrs['field']}"
            )
        return attrs


class TranslateAIContentApi(APIView):
    """POST /api/hr/translate/ — Translate AI-generated content to a target language."""

    permission_classes = [HasHRPermission]

    def post(self, request: Request) -> Response:
        if not _check_rate_limit(str(request.user.id)):
            return Response(
                {"detail": "Rate limit exceeded. Max 50 translation requests per hour."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = TranslateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        translated_text = translate_ai_content(
            model_name=data["model"],
            object_id=data["object_id"],
            field_name=data["field"],
            target_language=data["target_language"],
            user=request.user,
        )

        return Response(
            {"translated_text": translated_text, "language": data["target_language"]},
            status=status.HTTP_200_OK,
        )


class BatchTranslateApi(APIView):
    """POST /api/hr/translate/batch/ — Translate all criteria or questions for a vacancy step."""

    permission_classes = [HasHRPermission]

    class InputSerializer(serializers.Serializer):
        vacancy_id = serializers.UUIDField()
        item_type = serializers.ChoiceField(choices=["criteria", "questions"])
        step = serializers.ChoiceField(choices=["prescanning", "interview"])
        target_language = serializers.ChoiceField(choices=["en", "ru", "uz"])

    def post(self, request: Request) -> Response:
        if not _check_rate_limit(str(request.user.id)):
            return Response(
                {"detail": "Rate limit exceeded. Max 50 translation requests per hour."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            results = batch_translate_vacancy_items(
                item_type=data["item_type"],
                vacancy_id=data["vacancy_id"],
                step=data["step"],
                target_language=data["target_language"],
                user=request.user,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"items": results, "language": data["target_language"]},
            status=status.HTTP_200_OK,
        )
