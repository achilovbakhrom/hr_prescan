from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import get_or_create_candidate_profile
from apps.accounts.models import Certification
from apps.accounts.permissions import IsCandidate


class CertificationListCreateApi(APIView):
    """
    GET  /api/candidate/profile/certifications/ — list certifications.
    POST /api/candidate/profile/certifications/ — create certification.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        issuing_organization = serializers.CharField(
            max_length=255,
            required=False,
            allow_blank=True,
            default="",
        )
        issue_date = serializers.DateField(required=False, allow_null=True, default=None)
        expiry_date = serializers.DateField(required=False, allow_null=True, default=None)
        credential_url = serializers.URLField(
            max_length=500,
            required=False,
            allow_blank=True,
            default="",
        )
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        issuing_organization = serializers.CharField()
        issue_date = serializers.DateField()
        expiry_date = serializers.DateField()
        credential_url = serializers.CharField()
        image = serializers.CharField()
        order = serializers.IntegerField()

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.certifications.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = Certification.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CertificationDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/certifications/<id>/ — update.
    DELETE /api/candidate/profile/certifications/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        issuing_organization = serializers.CharField(
            max_length=255,
            required=False,
            allow_blank=True,
        )
        issue_date = serializers.DateField(required=False, allow_null=True)
        expiry_date = serializers.DateField(required=False, allow_null=True)
        credential_url = serializers.URLField(
            max_length=500,
            required=False,
            allow_blank=True,
        )
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        issuing_organization = serializers.CharField()
        issue_date = serializers.DateField()
        expiry_date = serializers.DateField()
        credential_url = serializers.CharField()
        image = serializers.CharField()
        order = serializers.IntegerField()

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.certifications.get(pk=pk)
        except Certification.DoesNotExist:
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
