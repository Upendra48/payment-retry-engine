#!/bin/sh
set -e

python manage.py migrate

python manage.py collectstatic --noinput

PORT=${PORT:-8000}

gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT