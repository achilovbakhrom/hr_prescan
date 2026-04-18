from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.apis.candidate_serializers import CandidateProfileOutputSerializer
from apps.accounts.cv_services import (
    improve_cv_section,
    parse_cv_with_ai,
)
from apps.accounts.models import CandidateProfile
from apps.accounts.permissions import IsCandidate


class CvParseApi(APIView):
    """POST /api/candidate/profile/cv/parse/ — upload CV file, AI parses and populates profile."""

    permission_classes = [IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        cv_file = request.FILES.get("cv_file")
        if not cv_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if cv_file.size > max_size:
            return Response(
                {"detail": "File too large. Maximum 10 MB."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        ext = cv_file.name.rsplit(".", 1)[-1].lower() if "." in cv_file.name else ""
        if ext not in ("pdf", "docx"):
            return Response(
                {"detail": "Only PDF and DOCX files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_bytes = cv_file.read()
        profile = parse_cv_with_ai(
            user=request.user,
            file_bytes=file_bytes,
            filename=cv_file.name,
        )

        profile = (
            CandidateProfile.objects.select_related("user")
            .prefetch_related(
                "skills",
                "work_experiences",
                "educations__education_level",
                "languages__language",
                "certifications",
                "cvs",
            )
            .get(pk=profile.pk)
        )
        return Response(
            CandidateProfileOutputSerializer(profile).data,
            status=status.HTTP_200_OK,
        )


class CvImproveSectionApi(APIView):
    """POST /api/candidate/profile/cv/improve-section/ — AI improves a CV section."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        section = serializers.ChoiceField(choices=["summary", "experience_description"])
        content = serializers.CharField()
        job_title = serializers.CharField(required=False, allow_blank=True)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        improved = improve_cv_section(**serializer.validated_data)
        return Response({"improved": improved}, status=status.HTTP_200_OK)
