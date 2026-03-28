# HostAfrica VPS Deployment Guide (Django)

Follow these steps to deploy **BBInternational** on a HostAfrica VPS using Gunicorn and Nginx.

## 1. Server Setup
1. Log in via SSH: `ssh root@vps-ip`
2. Update system: `sudo apt update && sudo apt upgrade -y`
3. Install dependencies: `sudo apt install python3-pip python3-venv nginx postgresql libpq-dev -y`

## 2. Prepare Project
1. Clone your project or upload files to `/var/www/BBInternational`.
2. Create virtual environment:
   ```bash
   cd /var/www/BBInternational
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Update `.env` with VPS database credentials.

## 3. Database Migration
1. Create a PostgreSQL database and user.
2. Run migrations: `python manage.py migrate`
3. Load data: `python manage.py loaddata neon_backup_full_essential.json`
4. Collect static: `python manage.py collectstatic --noinput`

## 4. Setup Gunicorn
1. Install Gunicorn: `pip install gunicorn`
2. Create Gunicorn systemd service file: `/etc/systemd/system/gunicorn.service`
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/BBInternational
   ExecStart=/var/www/BBInternational/venv/bin/gunicorn --workers 3 --bind unix:/var/www/BBInternational/app.sock church_app.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```
3. Start and enable: `sudo systemctl start gunicorn && sudo systemctl enable gunicorn`

## 5. Configure Nginx
1. Create Nginx config: `/etc/nginx/sites-available/BBInternational`
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location /static/ {
           root /var/www/BBInternational;
       }

       location /media/ {
           root /var/www/BBInternational;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/BBInternational/app.sock;
       }
   }
   ```
2. Enable: `sudo ln -s /etc/nginx/sites-available/BBInternational /etc/nginx/sites-enabled`
3. Test and restart: `sudo nginx -t && sudo systemctl restart nginx`

## 6. Security & SSL
1. Install Certbot: `sudo apt install certbot python3-certbot-nginx -y`
2. Get SSL: `sudo certbot --nginx -d your-domain.com`
