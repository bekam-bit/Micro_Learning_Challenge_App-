#!/usr/bin/env bash
set -euo pipefail

# Script placed inside backend/ so Render can run it as 'bash backend/render-start.sh'

# Default WEB_CONCURRENCY if not set by the environment (Render sets it sometimes)
: "${WEB_CONCURRENCY:=1}"
export WEB_CONCURRENCY

echo "Using WEB_CONCURRENCY=${WEB_CONCURRENCY}"

echo "Waiting for DB and running migrations..."

n=0
until python manage.py migrate; do
  n=$((n+1))
  echo "migrate failed, retrying ($n)..."
  sleep 3
  if [ "$n" -ge 20 ]; then
    echo "migrate failed after $n attempts" >&2
    exit 1
  fi
done

# Collect static files
python manage.py collectstatic --noinput

# Create superuser non-interactively if env vars are provided
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "Ensuring superuser ${DJANGO_SUPERUSER_USERNAME} exists..."
  python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')

if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully.")
else:
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
EOF
else
  echo "DJANGO_SUPERUSER_USERNAME/PASSWORD not set; skipping superuser creation."
fi

# Start Gunicorn with the configured number of workers
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers "$WEB_CONCURRENCY"
