#!/bin/bash
set -e

# Wait for database availability (optional, relies on Cloud SQL Proxy in Cloud Run)
echo "Starting migration..."
python manage.py migrate
echo "Migration finished."
