from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import get_or_create_candidate_profile
from apps.accounts.models import Education
from apps.accounts.permissions import IsCandidate
from apps.common.models import EducationLevel


class EducationListCreateApi(APIView):
    """
    GET  /api/candidate/profile/educations/ — list educations.
    POST /api/candidate/profile/educations/ — create education.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        institution = serializers.CharField(max_length=255)
        degree = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        education_level = serializers.SlugField(max_length=50, required=False, allow_null=True, default=None)
        field_of_study = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        start_date = serializers.DateField(required=False, allow_null=True, default=None)
        end_date = serializers.DateField(required=False, allow_null=True, default=None)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        institution = serializers.CharField()
        degree = serializers.CharField()
        education_level = serializers.SerializerMethodField()
        field_of_study = serializers.CharField()
        start_date = serializers.DateField()
        end_date = serializers.DateField()
        description = serializers.CharField()
        order = serializers.IntegerField()

        def get_education_level(self, obj):
            if obj.education_level is None:
                return None
            return {"slug": obj.education_level.slug, "name": obj.education_level.name}

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.educations.select_related("education_level").all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = get_or_create_candidate_profile(user=request.user)

        education_level_slug = data.pop("education_level", None)
        education_level = None
        if education_level_slug:
            try:
                education_level = EducationLevel.objects.get(slug=education_level_slug)
            except EducationLevel.DoesNotExist:
                return Response(
                    {"detail": f"Education level '{education_level_slug}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        item = Education.objects.create(profile=profile, education_level=education_level, **data)
        item = Education.objects.select_related("education_level").get(pk=item.pk)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class EducationDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/educations/<id>/ — update.
    DELETE /api/candidate/profile/educations/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        institution = serializers.CharField(max_length=255, required=False)
        degree = serializers.CharField(max_length=255, required=False, allow_blank=True)
        education_level = serializers.SlugField(max_length=50, required=False, allow_null=True)
        field_of_study = serializers.CharField(max_length=255, required=False, allow_blank=True)
        start_date = serializers.DateField(required=False, allow_null=True)
        end_date = serializers.DateField(required=False, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True)
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        institution = serializers.CharField()
        degree = serializers.CharField()
        education_level = serializers.SerializerMethodField()
        field_of_study = serializers.CharField()
        start_date = serializers.DateField()
        end_date = serializers.DateField()
        description = serializers.CharField()
        order = serializers.IntegerField()

        def get_education_level(self, obj):
            if obj.education_level is None:
                return None
            return {"slug": obj.education_level.slug, "name": obj.education_level.name}

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.educations.select_related("education_level").get(pk=pk)
        except Education.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields = []

        # Handle education_level FK separately
        if "education_level" in data:
            education_level_slug = data.pop("education_level")
            if education_level_slug is None:
                item.education_level = None
            else:
                try:
                    item.education_level = EducationLevel.objects.get(slug=education_level_slug)
                except EducationLevel.DoesNotExist:
                    return Response(
                        {"detail": f"Education level '{education_level_slug}' not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            update_fields.append("education_level")

        for field, value in data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        item = Education.objects.select_related("education_level").get(pk=item.pk)
        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
