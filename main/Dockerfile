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
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy project files
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port for Gunicorn
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
