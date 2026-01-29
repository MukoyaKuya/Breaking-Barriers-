from django.db import migrations, models


def update_cta_school_of_ministry_url(apps, schema_editor):
    CTACard = apps.get_model('church', 'CTACard')
    try:
        cta = CTACard.objects.get(pk=1)
    except CTACard.DoesNotExist:
        return

    if (cta.button2_url or '').strip() in (
        '/childrens-bread-school/',
        'http://127.0.0.1:8080/childrens-bread-school/',
    ):
        cta.button2_url = '/school-of-ministry/'
        cta.save(update_fields=['button2_url'])


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0024_wordoftruth_author_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolMinistryEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programme', models.CharField(default='School of Ministry', help_text='Programme name (kept for reporting/future expansion)', max_length=100)),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=30)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'School Ministry Enrollment',
                'verbose_name_plural': 'School Ministry Enrollments',
                'ordering': ['-enrolled_at'],
            },
        ),
        migrations.RunPython(update_cta_school_of_ministry_url, migrations.RunPython.noop),
    ]

