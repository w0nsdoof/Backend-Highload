# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install PostgreSQL development dependencies first
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY config /app/config
COPY apps /app/apps
COPY manage.py /app/manage.py

# Create static directory
RUN mkdir -p /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port for Gunicorn
EXPOSE 8000

# Start Gunicorn
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "config.wsgi:application"]
