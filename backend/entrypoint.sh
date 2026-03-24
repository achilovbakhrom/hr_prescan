#!/bin/bash
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Register Telegram webhook if URL is configured (production only)
if [ -n "$TELEGRAM_WEBHOOK_URL" ] && [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  echo "Registering Telegram webhook..."
  python manage.py setup_telegram_webhook "$TELEGRAM_WEBHOOK_URL"
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-4} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
