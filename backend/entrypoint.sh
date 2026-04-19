#!/bin/bash
set -e

# If an explicit command was passed (e.g. celery, manage.py subcommand),
# run it directly so this image can back both web and worker services.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "Ensuring S3/MinIO bucket exists..."
python - <<'PY' || echo "[WARN] bucket bootstrap failed — continuing, collectstatic will surface it"
import os
import boto3
from botocore.exceptions import ClientError

endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
access = os.environ.get("MINIO_ACCESS_KEY") or os.environ.get("S3_ACCESS_KEY")
secret = os.environ.get("MINIO_SECRET_KEY") or os.environ.get("S3_SECRET_KEY")
bucket = os.environ.get("MINIO_BUCKET_NAME", "hr-prescan")

if not (access and secret):
    raise SystemExit("S3 credentials not set — skipping bucket bootstrap")

client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access,
    aws_secret_access_key=secret,
    region_name="us-east-1",
)

try:
    client.head_bucket(Bucket=bucket)
    print(f"Bucket already exists: {bucket}")
except ClientError as exc:
    status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 404:
        client.create_bucket(Bucket=bucket)
        print(f"Created bucket: {bucket}")
    else:
        raise
PY

echo "Refreshing GeoIP DB (no-op if up to date or license key missing)..."
python manage.py download_geoip || echo "[WARN] download_geoip failed — continuing without GeoIP"

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Register Telegram webhooks if URLs are configured (production only).
# Both bots are independent: register each one if its URL + token are present.
HR_URL="${TELEGRAM_HR_WEBHOOK_URL:-$TELEGRAM_WEBHOOK_URL}"
HR_TOKEN="${TELEGRAM_HR_BOT_TOKEN:-$TELEGRAM_BOT_TOKEN}"
if [ -n "$HR_URL" ] && [ -n "$HR_TOKEN" ]; then
  echo "Registering HR Telegram webhook..."
  python manage.py setup_telegram_webhook "$HR_URL" --role hr
fi

if [ -n "$TELEGRAM_CANDIDATE_WEBHOOK_URL" ] && [ -n "$TELEGRAM_CANDIDATE_BOT_TOKEN" ]; then
  echo "Registering Candidate Telegram webhook..."
  python manage.py setup_telegram_webhook "$TELEGRAM_CANDIDATE_WEBHOOK_URL" --role candidate
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-4} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
