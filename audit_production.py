import os, django, sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
django.setup()

from church.models import NewsItem, NewsLine, Verse, Book, ChildrensBread, WordOfTruth, ManTalk

results = []
for name, M in [('NewsItem',NewsItem),('NewsLine',NewsLine),('Verse',Verse),('Book',Book),('ChildrensBread',ChildrensBread),('WordOfTruth',WordOfTruth),('ManTalk',ManTalk)]:
    try:
        results.append(f"{name}: {M.objects.count()}")
    except Exception as e:
        results.append(f"{name}: ERR {e}")

with open('audit_result.txt','w') as f:
    f.write('\n'.join(results))
print("Done - see audit_result.txt")
