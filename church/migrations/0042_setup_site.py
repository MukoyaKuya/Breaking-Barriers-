from django.db import migrations

def create_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Use SITE_ID=1 as per settings.py
    site, created = Site.objects.get_or_create(id=1)
    site.domain = 'bb-international.org'
    site.name = 'Breaking Barriers International'
    site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('church', '0041_alter_galleryimage_image'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_site),
    ]
