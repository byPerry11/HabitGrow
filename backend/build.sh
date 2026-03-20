#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies based on user's typo-filename
pip install -r requierements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
