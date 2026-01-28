#!/bin/bash

# Substitute the environment variables in the nginx config
envsubst '$PORT $GS_BUCKET_NAME' < /app/nginx.conf.template > /app/nginx.conf

# Start Gunicorn in the background on port 8000
echo "Starting Gunicorn on port 8000..."
gunicorn --bind 127.0.0.1:8000 --workers 1 --threads 8 --timeout 0 church_app.wsgi:application &

# Start Nginx in the foreground
echo "Starting Nginx on port $PORT..."
nginx -c /app/nginx.conf -g "daemon off;"
