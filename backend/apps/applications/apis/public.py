
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import CandidateCV
from apps.applications.serializers import ApplicationDetailOutputSerializer
from apps.applications.services import submit_application, upload_cv_to_s3
from apps.common.exceptions import ApplicationError


class SubmitApplicationApi(APIView):
    """POST /api/public/vacancies/{vacancy_id}/apply/ — submit an application."""

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    class InputSerializer(serializers.Serializer):
        candidate_name = serializers.CharField(max_length=255)
        candidate_email = serializers.EmailField()
        candidate_phone = serializers.CharField(
            max_length=50, required=False, allow_blank=True, default="",
        )
        cv_file = serializers.FileField(required=False, allow_null=True, default=None)
        cv_id = serializers.UUIDField(required=False, allow_null=True, default=None)

    def _resolve_cv(self, request, data, vacancy_id):
        """Resolve CV from uploaded file or existing profile CV."""
        cv_file = data.pop("cv_file", None)
        cv_id = data.pop("cv_id", None)

        if cv_file and cv_id:
            raise ApplicationError("Provide either cv_file or cv_id, not both.")

        if cv_id:
            if not (request.user and request.user.is_authenticated):
                raise ApplicationError("Authentication required to use profile CV.")
            try:
                cv = CandidateCV.objects.select_related("profile").get(
                    pk=cv_id, profile__user=request.user,
                )
            except CandidateCV.DoesNotExist:
                raise ApplicationError("CV not found.")
            return cv.file, cv.name

        if cv_file:
            return upload_cv_to_s3(file_obj=cv_file, vacancy_id=vacancy_id), cv_file.name

        return "", ""

    def post(self, request: Request, vacancy_id: str) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            cv_file_path, cv_original_filename = self._resolve_cv(request, data, vacancy_id)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        candidate = None
        if request.user and request.user.is_authenticated:
            candidate = request.user

        try:
            result = submit_application(
                vacancy_id=vacancy_id,
                candidate=candidate,
                cv_file_path=cv_file_path,
                cv_original_filename=cv_original_filename,
                **data,
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application = result["application"]
        response_data = ApplicationDetailOutputSerializer(application).data
        response_data["prescan_token"] = result["prescan_token"]
        response_data["screening_mode"] = result["prescan_session"].screening_mode

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )
