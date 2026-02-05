from django.db import migrations, models
import ckeditor.fields
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0025_school_ministry_enrollment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='The birth of a Ministry', max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('image', models.ImageField(help_text='Image shown on the About page (e.g. founder photo)', upload_to='about/')),
                ('image_cropping', image_cropping.fields.ImageRatioField('image', '400x400', adapt_rotation=False, free_crop=False, help_text='Crop the image to a square for best results (400x400).', hide_image_field=False, size_warning=True, verbose_name='image cropping')),
                ('body', ckeditor.fields.RichTextField(help_text='Main About text. Supports headings, paragraphs and bullet lists.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'About Page',
                'verbose_name_plural': 'About Page',
            },
        ),
    ]

