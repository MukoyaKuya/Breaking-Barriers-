import os
import django
from django.core.management import call_command
from django.conf import settings
import sys

# Define Neon URL
NEON_DB_URL = "postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def sync_data():
    # 1. Setup Django with Neon Config to Dump
    print("--- Connecting to Neon DB for Dump ---")
    os.environ['DATABASE_URL'] = NEON_DB_URL
    # Force re-setup if needed, but usually we rely on process isolation. 
    # Since we can't easily change settings.DATABASES on the fly after django.setup(),
    # we might need to do this in two passes or hack defaults.
    
    # Actually, simpler to run dumpdata as a subprocess or just set env and run this script?
    # No, we are IN a python script.
    
    # We will try to modify settings on the fly for the dump phase?
    # Django settings are immutable-ish.
    
    # Better approach: This script Orchestrates two subprocesses.
    
    pass

if __name__ == "__main__":
    # We will use subprocess to ensure clean settings load for each phase
    import subprocess
    
    # Phase 1: Dump
    print(">>> DUMPING FROM NEON")
    env_dump = os.environ.copy()
    env_dump['DATABASE_URL'] = NEON_DB_URL
    # Ensure UTF-8 output on Windows
    env_dump['PYTHONIOENCODING'] = 'utf-8'
    
    # We use a python one-liner to dump to avoid shell redirection encoding issues
    dump_cmd = [
        sys.executable, '-X', 'utf8', 'manage.py', 'dumpdata', 
        '--exclude', 'auth.permission', 
        '--exclude', 'contenttypes',
        '--exclude', 'admin.logentry', 
        '--exclude', 'church.PageView',
        '--exclude', 'church.BoardMember',
        '--exclude', 'sessions.Session',
        '--indent', '2'
    ]
    
    try:
        with open('neon_data.json', 'w', encoding='utf-8') as f:
            p = subprocess.run(dump_cmd, env=env_dump, stdout=f, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            print(f"!!! DUMP FAILED (Code {p.returncode}):")
            print(p.stderr)
            sys.exit(1)
        else:
            print(">>> DUMP COMPLETE: neon_data.json")
    except Exception as e:
        print(f"!!! DUMP EXCEPTION: {e}")
        sys.exit(1)

    # Phase 2: Load to Local (SQLite)
    print(">>> LOADING TO LOCAL SQLITE")
    env_load = os.environ.copy()
    if 'DATABASE_URL' in env_load:
        del env_load['DATABASE_URL'] # Ensure we default to SQLite
        
    # Migrate first
    subprocess.run([sys.executable, 'manage.py', 'migrate'], env=env_load, check=True)
    
    # Flush existing data (interactive=False)
    # We need to be careful. flush removes EVERYTHING.
    print(">>> FLUSHING LOCAL DATA")
    subprocess.run([sys.executable, 'manage.py', 'flush', '--no-input'], env=env_load, check=True)
    
    # Load
    load_cmd = [sys.executable, 'manage.py', 'loaddata', 'neon_data.json']
    try:
        subprocess.run(load_cmd, env=env_load, check=True)
        print(">>> LOAD COMPLETE")
    except subprocess.CalledProcessError as e:
        print(f"!!! LOAD FAILED: {e}")
        sys.exit(1)

    # Verification
    print(">>> VERIFYING COUNTS")
    subprocess.run([sys.executable, 'manage.py', 'shell', '-c', 
                    "import django; django.setup(); from church.models import NewsItem, GalleryImage, Partner; print(f'News: {NewsItem.objects.count()}, Gallery: {GalleryImage.objects.count()}, Partners: {Partner.objects.count()}')"], 
                   env=env_load, check=True)
