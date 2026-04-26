import os

req_file = 'requirements.txt'
exclude = {'pycairo', 'py-ubjson', 'lxml', 'rlPyCairo', 'svglib', 'xhtml2pdf'}

# Try to read with different encodings
encodings = ['utf-16', 'utf-16le', 'utf-8', 'latin1']
lines = []

for enc in encodings:
    try:
        with open(req_file, 'r', encoding=enc) as f:
            lines = f.readlines()
        print(f"Successfully read with {enc}")
        break
    except (UnicodeDecodeError, LookupError):
        continue

if not lines:
    print("Could not read requirements.txt with any encoding.")
    exit(1)

new_lines = []
removed = []

for line in lines:
    clean_line = line.strip()
    if not clean_line:
        new_lines.append(line)
        continue
        
    # Check if the package (before ==) is in exclude list
    package = clean_line.split('==')[0].strip()
    if package in exclude:
        removed.append(package)
    else:
        new_lines.append(line)

with open(req_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Removed: {', '.join(removed)}")
print(f"Cleaned {req_file} and saved as UTF-8.")
