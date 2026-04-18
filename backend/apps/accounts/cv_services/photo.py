import uuid

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings

ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=BotoConfig(signature_version="s3v4"),
    )


def upload_profile_photo_to_s3(*, file_obj, user_id) -> str:
    """Upload a profile photo to S3/MinIO and return the object key."""
    ext = file_obj.name.rsplit(".", 1)[-1].lower() if "." in file_obj.name else "jpg"
    key = f"profile-photos/{user_id}/{uuid.uuid4()}.{ext}"

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": file_obj.content_type or "image/jpeg"},
    )
    return key


def delete_profile_photo_from_s3(*, key: str) -> None:
    if not key:
        return
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)


def generate_profile_photo_url(*, key: str, expiration: int = 3600) -> str:
    if not key:
        return ""
    s3 = _get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
        ExpiresIn=expiration,
    )
