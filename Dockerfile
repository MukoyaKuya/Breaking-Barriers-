# Use the official lightweight Python image.
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install nginx, gettext, and dos2unix (for line ending conversion)
RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    build-essential \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Convert Windows line endings to Unix in shell scripts
RUN dos2unix /app/scripts/*.sh

# Ensure media directory exists and has files
# Install production dependencies and collect static files.
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p media \
    && python manage.py collectstatic --noinput

# Setup start script
RUN chmod +x /app/scripts/start.sh && chmod +x /app/scripts/migrate.sh

# Run the startup script
CMD ["bash", "/app/scripts/start.sh"]
