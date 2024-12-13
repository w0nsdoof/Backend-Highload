# Build and start all services
1. Run `docker compose up --build`

# Apply database migrations
2. Open a shell in the Django container:
   ```bash
   docker compose exec django-1 bash
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

