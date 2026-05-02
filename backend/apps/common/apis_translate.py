import time
from collections import defaultdict

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission
from apps.common.services_translation import TRANSLATABLE_FIELDS, batch_translate_vacancy_items, translate_ai_content

# Simple in-memory rate limiter: max 50 requests per user per hour
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 50
RATE_LIMIT_WINDOW = 3600


def _check_rate_limit(key: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > window_start]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit_store[key].append(now)
    return True


def _rate_limit_key(request: Request) -> str:
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded_for.split(",", 1)[0].strip() or request.META.get("REMOTE_ADDR", "anonymous")
    return f"ip:{ip_address}"


class TranslateInputSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=50)
    object_id = serializers.UUIDField()
    field = serializers.CharField(max_length=50)
    target_language = serializers.ChoiceField(choices=["en", "ru", "uz"])
    share_token = serializers.UUIDField(required=False)

    def validate(self, attrs):
        key = (attrs["model"], attrs["field"])
        if key not in TRANSLATABLE_FIELDS:
            raise serializers.ValidationError(f"Invalid model/field combination: {attrs['model']}/{attrs['field']}")
        return attrs


def _do_translate(request: Request, public_only: bool) -> Response:
    if not _check_rate_limit(_rate_limit_key(request)):
        return Response(
            {"detail": "Rate limit exceeded. Max 50 translation requests per hour."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    serializer = TranslateInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if public_only:
        field_config = TRANSLATABLE_FIELDS[(data["model"], data["field"])]
        if not field_config.get("public", False):
            return Response(
                {"detail": "This field requires elevated permissions. Use /api/hr/translate/ instead."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not _can_translate_public_object(data):
            return Response(
                {"detail": "This content is not available for public translation."},
                status=status.HTTP_403_FORBIDDEN,
            )

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


def _can_translate_public_object(data: dict) -> bool:
    if data["model"] != "vacancy":
        return True

    from apps.vacancies.models import Vacancy

    try:
        vacancy = Vacancy.objects.only("id", "status", "visibility", "share_token").get(id=data["object_id"])
    except Vacancy.DoesNotExist:
        return False

    if vacancy.status != Vacancy.Status.PUBLISHED:
        return False
    if vacancy.visibility == Vacancy.Visibility.PUBLIC:
        return True
    return data.get("share_token") is not None and vacancy.share_token == data["share_token"]


class TranslateAIContentApi(APIView):
    """POST /api/hr/translate/ — Translate AI-generated content (HR-only)."""

    permission_classes = [HasHRPermission]

    def post(self, request: Request) -> Response:
        return _do_translate(request, public_only=False)


class TranslatePublicContentApi(APIView):
    """POST /api/translate/ — Translate public content (vacancy + employer fields).

    Any visitor can hit this endpoint. Private fields (interview scores,
    application notes) are rejected here — those require /api/hr/translate/.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        return _do_translate(request, public_only=True)


class BatchTranslateApi(APIView):
    """POST /api/hr/translate/batch/ — Translate all criteria or questions for a vacancy step."""

    permission_classes = [HasHRPermission]

    class InputSerializer(serializers.Serializer):
        vacancy_id = serializers.UUIDField()
        item_type = serializers.ChoiceField(choices=["criteria", "questions"])
        step = serializers.ChoiceField(choices=["prescanning", "interview"])
        target_language = serializers.ChoiceField(choices=["en", "ru", "uz"])

    def post(self, request: Request) -> Response:
        if not _check_rate_limit(_rate_limit_key(request)):
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
