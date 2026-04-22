#!/bin/bash
# ==============================================================
# BBI VPS Deployment Script
# For Ubuntu 22.04/24.04 on HostPinnacle VPS
# Run as root: sudo bash deploy.sh
# ==============================================================

set -e

# ---- Configuration (edit these before running) ----
DOMAIN="bb-international.org"
APP_USER="bbi"
APP_DIR="/home/$APP_USER/Breaking-Barriers"
REPO_URL="https://github.com/MukoyaKuya/Breaking-Barriers.git"
DB_NAME="bbi_prod"
DB_USER="bbi_user"
DB_PASS="$(openssl rand -base64 18)"
DJANGO_SECRET="$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9' | head -c 64)"

echo "============================================"
echo "  BBI VPS Deployment - HostPinnacle"
echo "============================================"
echo ""
echo "Domain:   $DOMAIN"
echo "App User: $APP_USER"
echo "App Dir:  $APP_DIR"
echo ""

# ---- 1. System Updates & Dependencies ----
echo "[1/8] Installing system dependencies..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git curl build-essential libpq-dev \
    libjpeg-dev zlib1g-dev libffi-dev

# ---- 2. Create App User ----
echo "[2/8] Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$APP_USER"
fi

# ---- 3. Setup PostgreSQL ----
echo "[3/8] Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true

# ---- 4. Clone Repository ----
echo "[4/8] Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "  Directory exists, pulling latest..."
    cd "$APP_DIR"
    sudo -u "$APP_USER" git pull origin main
else
    sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

# ---- 5. Python Virtual Environment & Dependencies ----
echo "[5/8] Setting up Python environment..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# ---- 6. Create Production .env ----
echo "[6/8] Creating production .env..."
cat > "$APP_DIR/.env" << EOF
DEBUG=False
SECRET_KEY=$DJANGO_SECRET
DATABASE_URL=postgres://$DB_USER:$DB_PASS@127.0.0.1:5432/$DB_NAME
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
GS_BUCKET_NAME=bbinternational-media
CUSTOM_DOMAIN=$DOMAIN
EOF
chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

# ---- 7. Django Setup ----
echo "[7/8] Running Django setup..."
cd "$APP_DIR"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" manage.py migrate --noinput
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" manage.py collectstatic --noinput

# Load production data if backup exists
if [ -f "$APP_DIR/neon_backup_full_essential.json" ]; then
    echo "  Loading production data..."
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" manage.py loaddata neon_backup_full_essential.json || true
fi

# ---- 8. Setup Gunicorn & Nginx ----
echo "[8/8] Configuring Gunicorn & Nginx..."

# Gunicorn systemd service
cat > /etc/systemd/system/bbi.service << EOF
[Unit]
Description=BBI Gunicorn Django App
After=network.target postgresql.service

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn church_app.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile $APP_DIR/logs/gunicorn-access.log \
    --error-logfile $APP_DIR/logs/gunicorn-error.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create logs directory
sudo -u "$APP_USER" mkdir -p "$APP_DIR/logs"

# Nginx site config
cat > /etc/nginx/sites-available/bbi << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Media files (fallback to GCS)
    location /media/ {
        alias $APP_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/bbi /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t && systemctl reload nginx
systemctl daemon-reload
systemctl enable bbi
systemctl start bbi

echo ""
echo "============================================"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "  Domain:     http://$DOMAIN"
echo "  App Dir:    $APP_DIR"
echo "  DB Name:    $DB_NAME"
echo "  DB User:    $DB_USER"
echo "  DB Pass:    $DB_PASS"
echo ""
echo "  SAVE THESE CREDENTIALS SECURELY!"
echo ""
echo "  Next steps:"
echo "  1. Point your domain DNS A record to this server's IP"
echo "  2. Run: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "  3. Check: sudo systemctl status bbi"
echo "  4. Logs:  tail -f $APP_DIR/logs/gunicorn-error.log"
echo ""
