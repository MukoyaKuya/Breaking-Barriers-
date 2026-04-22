import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
# No DATABASE_URL = uses local SQLite
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']
django.setup()

from church.models import NewsItem, NewsLine, Verse, Book, ChildrensBread, WordOfTruth, ManTalk

results = []
for name, M in [('NewsItem',NewsItem),('NewsLine',NewsLine),('Verse',Verse),('Book',Book),('ChildrensBread',ChildrensBread),('WordOfTruth',WordOfTruth),('ManTalk',ManTalk)]:
    try:
        results.append(f"{name}: {M.objects.count()}")
    except Exception as e:
        results.append(f"{name}: ERR {e}")

with open('local_audit_result.txt','w') as f:
    f.write('\n'.join(results))
print('\n'.join(results))
