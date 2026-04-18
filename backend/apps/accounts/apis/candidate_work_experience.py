from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import get_or_create_candidate_profile
from apps.accounts.models import CandidateProfile, WorkExperience
from apps.accounts.permissions import IsCandidate


class WorkExperienceListCreateApi(APIView):
    """
    GET  /api/candidate/profile/work-experiences/ — list work experiences.
    POST /api/candidate/profile/work-experiences/ — create work experience.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255)
        position = serializers.CharField(max_length=255)
        employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False,
            allow_blank=True,
            default="",
        )
        location = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        start_date = serializers.DateField()
        end_date = serializers.DateField(required=False, allow_null=True, default=None)
        is_current = serializers.BooleanField(required=False, default=False)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        company_name = serializers.CharField()
        position = serializers.CharField()
        employment_type = serializers.CharField()
        location = serializers.CharField()
        start_date = serializers.DateField()
        end_date = serializers.DateField()
        is_current = serializers.BooleanField()
        description = serializers.CharField()
        order = serializers.IntegerField()

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.work_experiences.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = WorkExperience.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class WorkExperienceDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/work-experiences/<id>/ — update.
    DELETE /api/candidate/profile/work-experiences/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255, required=False)
        position = serializers.CharField(max_length=255, required=False)
        employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False,
            allow_blank=True,
        )
        location = serializers.CharField(max_length=255, required=False, allow_blank=True)
        start_date = serializers.DateField(required=False)
        end_date = serializers.DateField(required=False, allow_null=True)
        is_current = serializers.BooleanField(required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        company_name = serializers.CharField()
        position = serializers.CharField()
        employment_type = serializers.CharField()
        location = serializers.CharField()
        start_date = serializers.DateField()
        end_date = serializers.DateField()
        is_current = serializers.BooleanField()
        description = serializers.CharField()
        order = serializers.IntegerField()

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.work_experiences.get(pk=pk)
        except WorkExperience.DoesNotExist:
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

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
