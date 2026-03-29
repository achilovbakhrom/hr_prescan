from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import get_or_create_candidate_profile
from apps.accounts.models import CandidateLanguage
from apps.accounts.permissions import IsCandidate
from apps.common.models import Language


class CandidateLanguageListCreateApi(APIView):
    """
    GET  /api/candidate/profile/languages/ — list languages.
    POST /api/candidate/profile/languages/ — create language entry.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        language = serializers.CharField(max_length=10)
        proficiency = serializers.ChoiceField(choices=CandidateLanguage.Proficiency.choices)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        language = serializers.SerializerMethodField()
        proficiency = serializers.CharField()

        def get_language(self, obj):
            return {"code": obj.language.code, "name": obj.language.name}

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.languages.select_related("language").all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = get_or_create_candidate_profile(user=request.user)

        language_code = data.pop("language")
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return Response(
                {"detail": f"Language '{language_code}' not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check uniqueness
        if profile.languages.filter(language=language).exists():
            return Response(
                {"detail": "This language has already been added to your profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = CandidateLanguage.objects.create(
            profile=profile, language=language, **data,
        )
        item = CandidateLanguage.objects.select_related("language").get(pk=item.pk)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CandidateLanguageDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/languages/<id>/ — update.
    DELETE /api/candidate/profile/languages/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        language = serializers.CharField(max_length=10, required=False)
        proficiency = serializers.ChoiceField(
            choices=CandidateLanguage.Proficiency.choices, required=False,
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        language = serializers.SerializerMethodField()
        proficiency = serializers.CharField()

        def get_language(self, obj):
            return {"code": obj.language.code, "name": obj.language.name}

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.languages.select_related("language").get(pk=pk)
        except CandidateLanguage.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields = []

        # Handle language FK separately
        if "language" in data:
            language_code = data.pop("language")
            try:
                item.language = Language.objects.get(code=language_code)
            except Language.DoesNotExist:
                return Response(
                    {"detail": f"Language '{language_code}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            update_fields.append("language")

        for field, value in data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        item = CandidateLanguage.objects.select_related("language").get(pk=item.pk)
        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
