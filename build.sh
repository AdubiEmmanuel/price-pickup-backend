#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files (if needed)
python manage.py collectstatic --no-input