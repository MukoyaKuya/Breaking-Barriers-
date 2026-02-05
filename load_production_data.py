import os
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_app.settings")
if "DATABASE_URL" in os.environ:
    del os.environ["DATABASE_URL"]

django.setup()

def load_data():
    dump_file = 'production_dump_2026_02_05.json'
    utf8_file = 'production_dump_utf8.json'
    
    try:
        print(f"Reading {dump_file} as binary to detect encoding...")
        with open(dump_file, 'rb') as f:
            raw = f.read()
            
        print(f"Header: {raw[:16].hex()}")
            
        content = None
        encoding_used = "unknown"
        
        # Strategy: Strip all null bytes and decode as UTF-8
        # This recovers UTF-8 content that was lazily expanded to UTF-16 by shell redirection
        print("Using Null-Strip strategy...")
        clean_raw = raw.replace(b'\x00', b'')
        
        # Remove BOM remnants if any (FF FE becomes FF FE which are valid bytes, but we want text)
        # If original was FF FE 5B 00...
        # Stripped: FF FE 5B...
        # UTF-8 decode of FF FE might fail?
        # Actually shell redirection usually writes BOM as bytes 0xFF 0xFE.
        # Stripping 00 keeps them.
        # We should slice them off if present.
        if clean_raw.startswith(b'\xff\xfe'):
            clean_raw = clean_raw[2:]
            
        try:
             content = clean_raw.decode('utf-8')
             encoding_used = 'null-strip-utf8'
        except UnicodeDecodeError:
             # Fallback: latin1?
             content = clean_raw.decode('latin1')
             encoding_used = 'null-strip-latin1'

        print(f"Decoded using {encoding_used}. Length: {len(content)}")
        print(f"Content Start: {content[:50]}") # Debug verification

        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Saved UTF-8 to {utf8_file}. Loading data...")
        call_command('loaddata', utf8_file)
            
        print(f"Saved UTF-8 to {utf8_file}. Loading data...")
        call_command('loaddata', utf8_file)
        print("Data loaded successfully.")

    except Exception as e:
        print(f"Error: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    load_data()
