from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import (
    generate_cv_pdf,
    get_or_create_candidate_profile,
)
from apps.accounts.models import CandidateCV
from apps.accounts.permissions import IsCandidate


class CandidateCVListCreateApi(APIView):
    """
    GET  /api/candidate/profile/cvs/ — list CVs.
    POST /api/candidate/profile/cvs/ — create CV entry.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False, default="My CV")
        template = serializers.CharField(max_length=50, required=False, default="classic")

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        template = serializers.CharField()
        file = serializers.CharField()
        is_active = serializers.BooleanField()
        created_at = serializers.DateTimeField()
        download_url = serializers.SerializerMethodField()

        def get_download_url(self, obj):
            if not obj.file:
                return None
            from apps.applications.services import generate_cv_download_url

            try:
                return generate_cv_download_url(cv_file_path=obj.file)
            except Exception:
                return None

    def get(self, request: Request) -> Response:
        from apps.accounts.models import CandidateProfile

        profile = CandidateProfile.objects.filter(user=request.user).first()
        if profile is None:
            return Response([], status=status.HTTP_200_OK)
        items = profile.cvs.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = CandidateCV.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CandidateCVDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/cvs/<id>/ — update CV metadata.
    DELETE /api/candidate/profile/cvs/<id>/ — delete CV.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        template = serializers.CharField(max_length=50, required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        template = serializers.CharField()
        file = serializers.CharField()
        is_active = serializers.BooleanField()
        created_at = serializers.DateTimeField()

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.cvs.get(pk=pk)
        except CandidateCV.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if item.is_active:
            return Response(
                {"detail": "Cannot delete an active CV. Deactivate it first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateCVActivateApi(APIView):
    """POST /api/candidate/profile/cvs/<id>/activate/ — toggle CV active state."""

    permission_classes = [IsCandidate]

    def post(self, request: Request, pk) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            cv = profile.cvs.get(pk=pk)
        except CandidateCV.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if cv.is_active:
            cv.is_active = False
            cv.save(update_fields=["is_active", "updated_at"])
            return Response({"detail": "CV deactivated.", "id": str(cv.id), "is_active": False})
        else:
            cv.activate()
            return Response({"detail": "CV activated.", "id": str(cv.id), "is_active": True})


class CvGeneratePdfApi(APIView):
    """POST /api/candidate/profile/cv/generate-pdf/ — generate PDF from profile."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        template = serializers.ChoiceField(
            choices=["classic", "modern", "minimal"],
            default="classic",
        )
        name = serializers.CharField(max_length=255, required=False, default="My CV")

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        cv, download_url = generate_cv_pdf(
            profile=profile,
            template_name=serializer.validated_data["template"],
            cv_name=serializer.validated_data["name"],
        )

        return Response(
            {
                "id": str(cv.id),
                "name": cv.name,
                "template": cv.template,
                "file": cv.file,
                "is_active": cv.is_active,
                "download_url": download_url,
            },
            status=status.HTTP_200_OK,
        )
