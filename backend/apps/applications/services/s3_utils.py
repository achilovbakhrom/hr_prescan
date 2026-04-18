import uuid

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=BotoConfig(signature_version="s3v4"),
    )


def upload_cv_to_s3(*, file_obj, vacancy_id) -> str:
    """Upload a CV file to S3/MinIO and return the object key."""
    ext = file_obj.name.rsplit(".", 1)[-1] if "." in file_obj.name else "pdf"
    prefix = (getattr(settings, "S3_KEY_PREFIX", "") or "").strip("/")
    base = f"cvs/{vacancy_id}/{uuid.uuid4()}.{ext}"
    key = f"{prefix}/{base}" if prefix else base

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": file_obj.content_type or "application/octet-stream"},
    )
    return key


def generate_cv_download_url(*, cv_file_path: str, expiration: int = 3600) -> str:
    """Generate a presigned URL for downloading a CV from S3/MinIO."""
    s3 = _get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": cv_file_path,
        },
        ExpiresIn=expiration,
    )
