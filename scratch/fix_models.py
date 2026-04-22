import os

path = r'c:\Users\Little Human\Desktop\BBInternational\Breaking-Barriers\church\models.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Testimonial (approx lines 243-257)
# We have:
# def get_embed_url(self):
#     """Return a YouTube embed URL if possible, or the raw URL as fallback."""
#     return _to_youtube_embed(self.video_url)
# 
# def get_youtube_thumbnail_url(self) -> str:
#     ...
#     return ''
# 
# 
# 
#     """Return a YouTube embed URL if possible, or the raw URL as fallback."""
#     return _to_youtube_embed(self.video_url)

# This is hard to regex exactly without knowing the spaces.
# I'll look for the specific duplicated docstring following a return ''

bad_segment = """        return ''



        \"\"\"Return a YouTube embed URL if possible, or the raw URL as fallback.\"\"\"
        return _to_youtube_embed(self.video_url)"""

# I'll try to find it with any whitespace
import re
pattern = re.compile(r'return \'\'\s+\"\"\"Return a YouTube embed URL if possible, or the raw URL as fallback\.\"\"\"\s+return _to_youtube_embed\(self\.video_url\)', re.MULTILINE)
content = pattern.sub("return ''", content)

# Also fix the one where def get_embed_url is followed immediately by def get_youtube...
# def get_embed_url(self):
# def get_youtube_thumbnail_url(self) -> str:
#     ...
#     return ''
# 
# 
#     """Return ..."""
#     return ...

pattern2 = re.compile(r'def get_embed_url\(self\):\s+def get_youtube_thumbnail_url\(self\) -> str:', re.MULTILINE)
# This one is tricky because we want to preserve get_youtube... but put get_embed_url correctly.

# Let's just define the correct blocks for the affected models and replace the whole mess.

def fix_model(name, docstring):
    pattern = re.compile(fr'class {name}\(models\.Model\):.*?def get_embed_url\(self\):.*?return _to_youtube_embed\(self\.video_url\)', re.DOTALL)
    # This might be too greedy.
    pass

# I'll just do a very simple string replacement for the exact messes I saw.

content = content.replace(
    '    def get_embed_url(self):\n    def get_youtube_thumbnail_url(self) -> str:',
    '    def get_youtube_thumbnail_url(self) -> str:'
)

# And fix the docstrings that are floating
content = content.replace(
    '        return \'\'\n\n\n        """Return a YouTube embed URL if possible, or the raw URL as fallback."""\n        return _to_youtube_embed(self.video_url)',
    '        return \'\''
)

content = content.replace(
    '        return \'\'\n\n\n        """Return YouTube embed URL if possible, or empty string."""\n        return _to_youtube_embed(self.video_url)',
    '        return \'\''
)

# Now I'll add the missing get_embed_url methods if they were deleted or messed up.
# Actually, I'll just write a clean version of the affected functions.

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
