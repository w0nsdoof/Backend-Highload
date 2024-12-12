import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    db_conn = connections['default']
    db_conn.cursor()
    print("Database connection successful.")
except OperationalError as e:
    print(f"OperationalError : {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
