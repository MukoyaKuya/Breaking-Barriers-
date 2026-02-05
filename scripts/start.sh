#!/bin/bash
set -x

# Substitute the environment variables in the nginx config
envsubst '$PORT $GS_BUCKET_NAME' < /app/nginx.conf.template > /app/nginx.conf

# Run migrations on boot to ensure DB is up to date (including sites/sitemaps)
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
  church_app.wsgi:application &

# Wait for Gunicorn to start serving connections
echo "Waiting for Gunicorn to be ready..."
timeout=30
while ! python -c "import socket; import sys; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); result = s.connect_ex(('127.0.0.1', 8000)); s.close(); sys.exit(result)" > /dev/null 2>&1; do
    timeout=$((timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo "Timed out waiting for Gunicorn to start."
        exit 1
    fi
    echo "Waiting for Gunicorn... ($timeout)"
    sleep 1
done

echo "Gunicorn started successfully."

# Start Nginx in the foreground
echo "Starting Nginx on port $PORT..."
nginx -c /app/nginx.conf -g "daemon off;"
