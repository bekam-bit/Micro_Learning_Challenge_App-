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
  python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User=get_user_model(); u=os.environ.get('DJANGO_SUPERUSER_USERNAME'); p=os.environ.get('DJANGO_SUPERUSER_PASSWORD'); e=os.environ.get('DJANGO_SUPERUSER_EMAIL',''); if u and p and not User.objects.filter(username=u).exists(): User.objects.create_superuser(u,e,p)"
else
  echo "DJANGO_SUPERUSER_USERNAME/PASSWORD not set; skipping superuser creation."
fi

# Start Gunicorn with the configured number of workers
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers "$WEB_CONCURRENCY"
