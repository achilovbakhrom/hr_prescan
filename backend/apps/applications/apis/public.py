from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.serializers import ApplicationDetailOutputSerializer
from apps.applications.services import submit_application
from apps.common.exceptions import ApplicationError


class SubmitApplicationApi(APIView):
    """POST /api/public/vacancies/{vacancy_id}/apply/ — submit an application."""

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        candidate_name = serializers.CharField(max_length=255)
        candidate_email = serializers.EmailField()
        candidate_phone = serializers.CharField(
            max_length=50, required=False, allow_blank=True, default="",
        )
        cv_file_path = serializers.CharField(
            max_length=500, required=False, allow_blank=True, default="",
        )
        cv_original_filename = serializers.CharField(
            max_length=255, required=False, allow_blank=True, default="",
        )

    def post(self, request: Request, vacancy_id: str) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If user is authenticated, attach as candidate
        candidate = None
        if request.user and request.user.is_authenticated:
            candidate = request.user

        try:
            application = submit_application(
                vacancy_id=vacancy_id,
                candidate=candidate,
                **serializer.validated_data,
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )
