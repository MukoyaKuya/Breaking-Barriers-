import os
import sys

# Set up the path to the project
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Initialize PyMySQL
try:
    import pymysql
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()
    
    # Monkeypatch Django's MySQL features to disable RETURNING clause
    from django.db.backends.mysql.features import DatabaseFeatures
    DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
    DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
except Exception:
    pass

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

# Import the Django WSGI application
from church_app.wsgi import application

# If the server expects 'application' as the variable name, we are good.
# Some cPanel setups might require 'application = wsgi.application' if it's not exported.
