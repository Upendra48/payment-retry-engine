#!/bin/sh
set -e

celery -A config worker \
    --loglevel=info \
    --concurrency=1 \
    --pool=solo