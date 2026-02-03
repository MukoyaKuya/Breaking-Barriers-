import psycopg2
import os

NEON_URL = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'

def check_raw():
    try:
        conn = psycopg2.connect(NEON_URL)
        cur = conn.cursor()
        cur.execute("SELECT username, password, is_active, is_staff, is_superuser FROM auth_user WHERE username = 'Roy';")
        row = cur.fetchone()
        if row:
            print(f"User: {row[0]}")
            print(f"Hash: {row[1]}")
            print(f"Active: {row[2]}, Staff: {row[3]}, Super: {row[4]}")
        else:
            print("User 'Roy' NOT FOUND in raw check.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_raw()
