#!/bin/sh
set -e

celery -A config beat -l info