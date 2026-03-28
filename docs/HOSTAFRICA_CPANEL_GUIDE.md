# HostAfrica cPanel Deployment Guide (Django)

Follow these steps to deploy **BBInternational** on HostAfrica Shared Hosting using cPanel.

## 1. Upload Files
1. Log in to cPanel.
2. Open **File Manager**.
3. Create a folder named `BBInternational` in your home directory (not inside `public_html`).
4. Upload your project files (including `.env`, `passenger_wsgi.py`, and `neon_backup_full_essential.json`) into this folder.

## 2. Setup Python App
1. In cPanel, search for **Setup Python App**.
2. Click **Create Application**.
3. **Python Version**: Select 3.9 or higher (matches your requirements).
4. **Application root**: `BBInternational`
5. **Application URL**: Select your domain.
6. **Application startup file**: `passenger_wsgi.py`
7. **Application Entry point**: `application`
8. Click **Create**.

## 3. Install Dependencies
1. Scroll down to the **Configuration files** section.
2. In the "Run pip install" box, select `requirements.txt` and click **Run pip install**.
3. Alternatively, copy the command shown at the top of the page (something like `source /home/username/nodevenv/.../bin/activate`) and run it in the **Terminal** in cPanel.

## 4. Configure Database
1. Go to **MySQL® Databases** (or PostgreSQL if supported) in cPanel.
2. Create a new database and user.
3. Update your `.env` file in the `BBInternational` folder with the new `DATABASE_URL`:
   `mysql://user:pass@localhost/dbname` (or use specific credentials).

## 5. Migrate Data
1. Open the **Terminal** in cPanel.
2. Navigate to your project root: `cd BBInternational`
3. Activate the virtual environment (use the command from "Setup Python App").
4. Run migrations: `python manage.py migrate`
5. Load the Neon data: `python manage.py loaddata neon_backup_full_essential.json`

## 6. Static Files
1. Run: `python manage.py collectstatic --noinput`
2. Ensure the static files are accessible via your domain. You may need to create a symbolic link from `public_html/static` to `BBInternational/staticfiles`.

## Troubleshooting
- **Logs**: Check `logs/django.log` in your project folder.
- **Errors**: Ensure `DEBUG=True` only during initial setup to see errors.
