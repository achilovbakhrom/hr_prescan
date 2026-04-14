#!/bin/bash
set -e

# If an explicit command was passed (e.g. celery, manage.py subcommand),
# run it directly so this image can back both web and worker services.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-4} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
