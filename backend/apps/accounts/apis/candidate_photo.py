from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import (
    ALLOWED_PHOTO_CONTENT_TYPES,
    ALLOWED_PHOTO_EXTENSIONS,
    MAX_PHOTO_SIZE_BYTES,
    delete_profile_photo_from_s3,
    generate_profile_photo_url,
    get_or_create_candidate_profile,
    upload_profile_photo_to_s3,
)
from apps.accounts.permissions import IsCandidate


class CandidateProfilePhotoApi(APIView):
    """POST / DELETE /api/candidate/profile/photo/ — upload or remove profile photo."""

    permission_classes = [IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        photo = request.FILES.get("photo")
        if not photo:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if photo.size > MAX_PHOTO_SIZE_BYTES:
            return Response(
                {"detail": "File too large. Maximum 5 MB."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        ext = photo.name.rsplit(".", 1)[-1].lower() if "." in photo.name else ""
        content_type = (photo.content_type or "").lower()
        if ext not in ALLOWED_PHOTO_EXTENSIONS or content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
            return Response(
                {"detail": "Only JPEG, PNG, or WEBP images are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_or_create_candidate_profile(user=request.user)
        previous_key = profile.photo

        key = upload_profile_photo_to_s3(file_obj=photo, user_id=request.user.id)
        profile.photo = key
        profile.save(update_fields=["photo", "updated_at"])

        if previous_key and previous_key != key:
            try:
                delete_profile_photo_from_s3(key=previous_key)
            except Exception:  # noqa: BLE001 — best-effort cleanup
                pass

        return Response(
            {"photo": key, "photo_url": generate_profile_photo_url(key=key)},
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        previous_key = profile.photo
        if not previous_key:
            return Response(status=status.HTTP_204_NO_CONTENT)

        profile.photo = ""
        profile.save(update_fields=["photo", "updated_at"])

        try:
            delete_profile_photo_from_s3(key=previous_key)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
