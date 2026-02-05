from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0026_about_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpage',
            name='video_url',
            field=models.URLField(blank=True, help_text='Optional YouTube video URL (e.g. https://www.youtube.com/watch?v=VIDEO_ID or https://www.youtube.com/embed/VIDEO_ID). If provided, video will be shown instead of or alongside the image.'),
        ),
        migrations.AlterField(
            model_name='aboutpage',
            name='image',
            field=models.ImageField(blank=True, help_text='Image shown on the About page (e.g. founder photo)', null=True, upload_to='about/'),
        ),
    ]
