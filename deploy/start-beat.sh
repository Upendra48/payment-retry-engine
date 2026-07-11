#!/bin/sh
set -e

celery -A config beat --loglevel=info