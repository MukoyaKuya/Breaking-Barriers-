#!/bin/bash

# Substitute the environment variables in the nginx config
envsubst '$PORT $GS_BUCKET_NAME' < /app/nginx.conf.template > /app/nginx.conf

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Gunicorn: (2 * CPU) + 1 workers recommended; default 5 workers, 4 threads
WORKERS=${GUNICORN_WORKERS:-5}
THREADS=${GUNICORN_THREADS:-4}
echo "Starting Gunicorn with $WORKERS workers and $THREADS threads..."
gunicorn \
  --bind 127.0.0.1:8000 \
  --workers "$WORKERS" \
  --threads "$THREADS" \
  --worker-class gthread \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --preload \
  church_app.wsgi:application &

# Start Nginx in the foreground
echo "Starting Nginx on port $PORT..."
nginx -c /app/nginx.conf -g "daemon off;"
