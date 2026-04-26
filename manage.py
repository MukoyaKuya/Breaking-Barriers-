#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Check if .env exists and load it
    try:
        import dotenv
        dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    except ImportError:
        pass
        
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

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
