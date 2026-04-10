#!/bin/bash
set -e

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
