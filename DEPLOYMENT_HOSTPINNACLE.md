# Breaking Barriers International - HostPinnacle Deployment Guide

This document is the definitive guide to deploying the "Breaking Barriers" Django application to a **HostPinnacle Standard Package** (Shared Hosting with cPanel & CloudLinux).

It is written specifically for the state of the codebase as of April 2026, taking into consideration the migration from Neon DB to local SQLite, and eventually to HostPinnacle's MySQL, as well as the transition from Google Cloud Storage to local NVMe SSDs.

---

## Phase 1: Local Preparation

Before touching your HostPinnacle account, you must package the local codebase.

1. **Clean the Codebase:**
   Delete the following folders from your local `Breaking-Barriers` folder to save space and avoid Linux conflicts:
   - `venv` (Virtual environment is OS-specific; you will create a new one on the server).
   - `__pycache__` folders (if visible).
   
2. **Ensure Export File Exists:**
   Make sure the `hostpinnacle_export.json` file is present in the root folder. This file contains all your synchronized production texts, articles, and users.

3. **Zip the Project:**
   Select all files inside the `Breaking-Barriers` folder, right-click, and select **Compress to ZIP file**. Name it `breaking_barriers_deploy.zip`.

---

## Phase 2: HostPinnacle cPanel Setup

Once you have purchased the Standard Package and your domain is active, log into your HostPinnacle cPanel.

### 1. Database Configuration
1. Navigate to **MySQL Databases** in cPanel.
2. Create a new database: e.g., `bbi_maindb`.
3. Create a new user: e.g., `bbi_dbuser`. Generate a highly secure password and save it.
4. **Important:** Add the user to the database and check the box for **"All Privileges"**.

### 2. Uploading the Code
1. Navigate to the **File Manager**.
2. Go to the root of your domain (usually `/home/yourusername/` or `public_html`).
3. Upload `breaking_barriers_deploy.zip` and extract it into a folder named `Breaking-Barriers`.
4. Delete the `.zip` file after extraction to save space.

### 3. Environment Variables
1. Inside the extracted folder, find the `production.env.example` file.
2. Rename it to exactly `.env`.
3. Edit the file inside cPanel to include your new database credentials:
   ```env
   # Inside .env
   DB_NAME=yourcpanelusername_bbi_maindb
   DB_USER=yourcpanelusername_bbi_dbuser
   DB_PASS=YourSuperSecretPassword
   DB_HOST=localhost
   DB_PORT=3306

   # Critical Settings for Standard Package
   USE_LOCAL_STORAGE=True
   DEBUG=False
   ```

---

## Phase 3: Setup Python App (Phusion Passenger)

HostPinnacle uses Phusion Passenger to serve Python apps securely on LiteSpeed.

1. In the main cPanel search bar, search for **"Setup Python App"**.
2. Click **Create Application**.
3. **Configuration:**
   - **Python Version:** Select `3.10` or higher.
   - **Application root:** Enter `Breaking-Barriers`.
   - **Application URL:** Choose your domain name.
   - **Application startup file:** `passenger_wsgi.py`.
   - **Application Entry point:** `application`.
4. Click **Create**.

*Once created, at the top of the screen, HostPinnacle will show you a command to enter the virtual environment. It looks something like:*
`source /home/username/virtualenv/Breaking-Barriers/3.10/bin/activate`
**Copy this command.**

---

## Phase 4: Final Execution (cPanel Terminal)

You now need to install the dependencies and migrate the database.

1. In cPanel, search for **Terminal** and open it.
2. Paste the `source...` command you copied in the previous step and hit Enter. Your terminal prompt should now have `(Breaking-Barriers:3.10)` at the beginning.
3. Navigate to your app directory if not there already:
   ```bash
   cd Breaking-Barriers
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations (Creates MySQL Tables):**
   ```bash
   python manage.py migrate
   ```

6. **Import Production Data:**
   Load the synchronized text content from the JSON export:
   ```bash
   python manage.py loaddata hostpinnacle_export.json
   ```

7. **Collect Static Files:**
   This bundles CSS, JavaScript, and fonts for production:
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Restart the App:**
   Go back to the **Setup Python App** page in cPanel and click the **Restart** button for your application.

---

## Phase 5: The Image Workaround

Because Google Cloud Storage was locked during the synchronization phase over a billing delinquency, the newly uploaded images trapped in Google Cloud could not be downloaded in bulk.

**To fix missing images on the live site:**
1. Navigate to your live website admin portal (`https://yourdomain.com/office/`).
2. Log in using your existing superuser credentials (they were transferred securely within the JSON export!).
3. Go to the **Gallery** and **Articles** sections.
4. Manually re-upload the latest images for the corrupted posts directly from your computer. Because `USE_LOCAL_STORAGE=True` is set, these images will elegantly save right to HostPinnacle's 100GB SSD perfectly.

> [!TIP]
> Everything regarding SEO, URLs, user accounts, and layout will be exactly as it was on the live site. Only the images need this manual touch.

### 🌐 Congratulations, your site is Live!
