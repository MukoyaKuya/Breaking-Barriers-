# Use the official lightweight Python image.
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install nginx and gettext (for envsubst)
RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Ensure media directory exists and has files
# Install production dependencies and collect static files.
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p media \
    && python manage.py collectstatic --noinput

# Setup start script
RUN chmod +x /app/scripts/start.sh

# Run the startup script
CMD ["/app/scripts/start.sh"]
