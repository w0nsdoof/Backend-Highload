#!/bin/sh

# Run Django management commands
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create log directory and file if not exists
mkdir -p /var/log/django
touch /var/log/django/django.log

# Start Gunicorn on the correct port
exec gunicorn -w 3 -b 0.0.0.0:${PORT:-8000} config.wsgi:application