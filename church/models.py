from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from urllib.parse import urlparse, parse_qs
from image_cropping import ImageRatioField


class Verse(models.Model):
    """Model for daily/weekly Bible verses"""
    content = models.TextField()
    reference = models.CharField(max_length=200)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_posted']
        verbose_name = 'Verse'
        verbose_name_plural = 'Verses'
        indexes = [
            models.Index(fields=['is_active', 'is_featured', '-date_posted']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.content[:50]}..."


class NewsItem(models.Model):
    """Model for news articles and events"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    image = models.ImageField(upload_to='news/')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image to your desired size')
    summary = models.TextField()
    body = RichTextField()
    event_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'News Item'
        verbose_name_plural = 'News Items'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news_detail', args=[self.slug])



class NewsLine(models.Model):
    """Model for News Line items (posters and videos)"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    image = models.ImageField(upload_to='news_line/', help_text='Poster image')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image to your desired size')
    video_url = models.URLField(
        blank=True,
        help_text='Optional YouTube video URL (e.g. https://www.youtube.com/watch?v=VIDEO_ID). If provided, video will be shown.',
    )
    summary = models.TextField(help_text='Short description or summary')
    body = RichTextField(blank=True, help_text='Full article content')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'News Line Item'
        verbose_name_plural = 'News Line Items'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_embed_url(self):
        """Return a YouTube embed URL if possible, or the raw URL as fallback."""
        return _to_youtube_embed(self.video_url)

    @property
    def created_at_month(self):
        """Month abbreviation (e.g. Jan) for badge display. Avoids date filter issues in templates."""
        return self.created_at.strftime('%b') if self.created_at else ''

    @property
    def created_at_day(self):
        """Day number (e.g. 01) for badge display."""
        return self.created_at.strftime('%d') if self.created_at else ''

    @property
    def created_at_long(self):
        """Full date string for video items."""
        return self.created_at.strftime('%B %d, %Y') if self.created_at else ''




class PartnerInquiry(models.Model):
    """Model for partnership inquiries from the Donate page."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, help_text='Phone number')
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Partner Inquiry'
        verbose_name_plural = 'Partner Inquiries'

    def __str__(self):
        return f"Partner Inquiry from {self.first_name} {self.last_name}"


class ContactMessage(models.Model):
    """Model for storing contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, help_text='Phone number')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"


class CalendarEvent(models.Model):

    """Interactive calendar event/task model"""
    EVENT_TYPE_CHOICES = [
        ('Service', 'Service'),
        ('Prayer Meeting', 'Prayer Meeting'),
        ('Outreach', 'Outreach'),
        ('Conference', 'Conference'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=200, help_text="Event or task title")
    description = models.TextField(blank=True, help_text="Optional description")
    event_date = models.DateField(help_text="Date of the event")
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default='Other',
        help_text="Type of event"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional location",
    )
    image = models.ImageField(
        upload_to='calendar_events/',
        blank=True,
        null=True,
        help_text="Optional image for the event (will be displayed in event details)",
    )
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image to your desired size')
    color = models.CharField(
        max_length=7,
        default='#990030',
        help_text="Color code for the event label (hex format, e.g. #990030)",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date', 'title']
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        indexes = [
            models.Index(fields=['event_date', 'is_published']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.event_date}"


class Testimonial(models.Model):
    """Model for member testimonials"""
    member_name = models.CharField(max_length=100)
    photo = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text='Optional image shown when no video is provided',
    )
    photo_cropping = ImageRatioField('photo', '400x400', size_warning=True, help_text='Crop the photo to your desired size')
    video_url = models.URLField(
        blank=True,
        help_text='Optional video URL (e.g. YouTube embed link)',
    )
    text = models.TextField(help_text='Testimonial content')
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        indexes = [
            models.Index(fields=['approved', '-created_at']),
        ]

    def __str__(self):
        return f"{self.member_name} - {self.text[:50]}..."

    def get_embed_url(self):
        """Return a YouTube embed URL if possible, or the raw URL as fallback."""
        return _to_youtube_embed(self.video_url)


class GalleryImage(models.Model):
    """Model for gallery images and videos"""
    CATEGORY_CHOICES = [
        ('Worship', 'Worship'),
        ('Outreach', 'Outreach'),
        ('Community', 'Community'),
        ('Events', 'Events'),
        ('Other', 'Other'),
    ]

    caption = models.CharField(max_length=200)
    image = models.FileField(upload_to='gallery/', help_text='Image or thumbnail for this item')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image to your desired size')
    video_url = models.URLField(
        blank=True,
        help_text='Optional video URL (e.g. YouTube embed link for video items)',
    )
    duration_label = models.CharField(
        max_length=10,
        blank=True,
        help_text='Optional duration label shown in gallery list (e.g. "0:16")',
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
        indexes = [
            models.Index(fields=['category', '-uploaded_at']),
        ]

    def __str__(self):
        return f"{self.caption} - {self.category}"

    def get_embed_url(self):
        """Return a YouTube embed URL if possible, or the raw URL as fallback."""
        return _to_youtube_embed(self.video_url)

    def get_youtube_thumbnail_url(self) -> str:
        """Return YouTube thumbnail URL (hqdefault) when video_url is a YouTube link. Empty string otherwise."""
        video_id = _youtube_video_id(self.video_url)
        if video_id:
            return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        return ''

    def get_image_url(self) -> str:
        """
        Return a usable image URL if the image is set.
        Avoids expensive storage existence checks in list views.
        """
        try:
            if self.image and self.image.name:
                return self.image.url
        except Exception:
            return ''
        return ''


class HeroSettings(models.Model):
    """Singleton model for hero section settings"""
    image = models.ImageField(upload_to='hero/', help_text='Background image for the hero section')
    image_cropping = ImageRatioField('image', '1920x1080', size_warning=True, help_text='Crop the hero image to your desired size')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Settings'
        verbose_name_plural = 'Hero Settings'

    def __str__(self):
        return "Hero Section Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AboutPage(models.Model):
    """Singleton model for the About Us page (story + founder image)."""
    title = models.CharField(max_length=200, default='The birth of a Ministry')
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to='about/',
        blank=True,
        null=True,
        help_text='Image shown on the About page (e.g. founder photo)',
    )
    image_cropping = ImageRatioField(
        'image',
        '400x400',
        size_warning=True,
        help_text='Crop the image to a square for best results (400x400).',
    )
    video_url = models.URLField(
        blank=True,
        help_text='Optional YouTube video URL (e.g. https://www.youtube.com/watch?v=VIDEO_ID or https://www.youtube.com/embed/VIDEO_ID). If provided, video will be shown instead of or alongside the image.',
    )
    body = RichTextField(
        help_text='Main About text. Supports headings, paragraphs and bullet lists.'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Page'
        verbose_name_plural = 'About Page'

    def __str__(self):
        return "About Page Content"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    def get_embed_url(self):
        """Return a YouTube embed URL if possible, or the raw URL as fallback."""
        return _to_youtube_embed(self.video_url)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'The birth of a Ministry',
                'body': (
                    "<p>A 20-year journey in the school of the Holy Spirit gave birth to the BBI Ministry. "
                    "In the area of deliverance the first thing that the Holy Spirit taught the founder, pastor Nellie Shani, "
                    "was about generational curses and how the sins of the forefathers could still affect us today.</p>"
                    "<p>Since then the founder has been involved in teaching around the world. "
                    "The first meeting before BBI was formally registered took place at her residence, "
                    "but later as the numbers grew she looked for a hall she could hire.</p>"
                    "<p>Ten days later we had an executive committee and a registered ministry called BBI in 2012. "
                    "Since then God has continued to add people who work with her and share the vision, "
                    "and many volunteers and partners have put their hand to the plough.</p>"
                    "<h3>Objectives</h3>"
                    "<ol>"
                    "<li>To teach Biblical truths concerning spiritual warfare and deliverance.</li>"
                    "<li>To help believers in Jesus Christ identify and break generational curses.</li>"
                    "<li>To enable believers in Jesus Christ know, live and sustain their deliverance.</li>"
                    "<li>To counsel believers in Jesus Christ who may need specialised help beyond the teaching and prayer seminars.</li>"
                    "<li>To identify and train workers in spiritual warfare and deliverance ministry.</li>"
                    "</ol>"
                ),
            },
        )
        return obj


class InfoCard(models.Model):
    """Model for info cards (Children's Bread, News, Word of Truth)"""
    CARD_TYPE_CHOICES = [
        ('childrens_bread', 'Children\'s Bread'),
        ('news', 'News'),
        ('word_of_truth', 'Word of Truth'),
    ]

    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, unique=True, 
                                 help_text='Type of card - only one card per type is displayed')
    title = models.CharField(max_length=200, help_text='Card title (e.g., "Children\'s Bread")')
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    image = models.ImageField(upload_to='info_cards/', help_text='Image displayed on the card')
    image_cropping = ImageRatioField('image', '1600x900', size_warning=True, help_text='Crop the image to 16:9 aspect ratio (1600x900) for proper display')
    headline = models.CharField(max_length=200, help_text='Bold headline text below the image')
    summary = models.TextField(help_text='Summary/description text (displayed on the homepage card)')
    content = RichTextField(blank=True, help_text='Full article content triggered by "Read More"')
    author_name = models.CharField(max_length=100, default='TechNurtures', 
                                  help_text='Author name displayed in metadata')
    link_url = models.CharField(max_length=200, blank=True, 
                               help_text='URL for "Read More" link (leave blank to use default)')
    is_active = models.BooleanField(default=True, help_text='Show this card on the homepage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['card_type']
        verbose_name = 'Info Card'
        verbose_name_plural = 'Info Cards'
        indexes = [
            models.Index(fields=['card_type', 'is_active']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.get_card_type_display()} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class WordOfTruth(models.Model):
    """Articles for Word of Truth section with PDF download"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    summary = models.TextField(help_text='Short summary for the listing page')
    author_name = models.CharField(max_length=100, default='Breaking Barriers International', help_text='Name of the article writer')
    image = models.ImageField(upload_to='word_of_truth/', blank=True, null=True, help_text='Featured image for the article')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image for proper display (800x600)')
    body = RichTextField(help_text='Full article content for the PDF and web view')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Word of Truth Article'
        verbose_name_plural = 'Word of Truth Articles'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('word_of_truth_detail', args=[self.slug])

    @property
    def created_at_month(self):
        """Month abbreviation (e.g. Jan) for badge display."""
        return self.created_at.strftime('%b') if self.created_at else ''

    @property
    def created_at_day(self):
        """Day number (e.g. 01) for badge display."""
        return self.created_at.strftime('%d') if self.created_at else ''


class ManTalk(models.Model):
    """Articles for ManTalk (formerly Men's Ministry)"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    summary = models.TextField(help_text='Short summary for the listing page')
    author_name = models.CharField(max_length=100, default='Breaking Barriers International', help_text='Name of the article writer')
    image = models.ImageField(upload_to='man_talk/', blank=True, null=True, help_text='Featured image for the article')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image for proper display (800x600)')
    body = RichTextField(help_text='Full article content')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ManTalk Article'
        verbose_name_plural = 'ManTalk Articles'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('mantalk_detail', args=[self.slug])

    @property
    def created_at_month(self):
        """Month abbreviation (e.g. Jan) for badge display."""
        return self.created_at.strftime('%b') if self.created_at else ''

    @property
    def created_at_day(self):
        """Day number (e.g. 01) for badge display."""
        return self.created_at.strftime('%d') if self.created_at else ''



class Book(models.Model):
    """Books with reviews and WhatsApp inquiry link"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    author = models.CharField(max_length=100, default='Pst. Nellie Shani', help_text='Author name', blank=True)
    cover_image = models.ImageField(upload_to='books/', help_text='Book cover image')
    image_cropping = ImageRatioField('cover_image', '600x900', size_warning=True, help_text='Crop for vertical book display (600x900)')
    description = models.TextField(help_text='Short description/summary for the card')
    review = RichTextField(help_text='Full book review and details')
    whatsapp_number = models.CharField(max_length=20, default='+254716703508', help_text='WhatsApp number for inquiries')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        # Invalidate book list cache
        from django.core.cache import cache
        cache.delete('book_list_all')

    @property
    def whatsapp_link(self):
        """Generate WhatsApp link for inquiries."""
        # Clean number (remove + or spaces if needed, but basic format works for wa.me)
        phone = self.whatsapp_number.replace('+', '').replace(' ', '')
        text = f"Hi, I'm interested in the book '{self.title}'."
        return f"https://wa.me/{phone}?text={text}"



class ChildrensBread(models.Model):
    """Articles for Children's Bread section"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    summary = models.TextField(help_text='Short summary for the listing page')
    author_name = models.CharField(max_length=100, default='Pst. Nellie Shani', help_text='Name of the article writer')
    image = models.ImageField(upload_to='childrens_bread/', blank=True, null=True, help_text='Featured image for the article')
    image_cropping = ImageRatioField('image', '800x600', size_warning=True, help_text='Crop the image for proper display (800x600)')
    body = RichTextField(help_text='Full article content')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Children's Bread Article"
        verbose_name_plural = "Children's Bread Articles"
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('childrens_bread_detail', args=[self.slug])

    @property
    def created_at_month(self):
        """Month abbreviation (e.g. Jan) for badge display."""
        return self.created_at.strftime('%b') if self.created_at else ''

    @property
    def created_at_day(self):
        """Day number (e.g. 01) for badge display."""
        return self.created_at.strftime('%d') if self.created_at else ''


class CTACard(models.Model):
    """Singleton model for Call-to-Action card (4th card)"""
    quote_text = models.TextField(help_text='Motivational quote text')
    verse_reference = models.CharField(max_length=50, default='Galatians 3:13',
                                      help_text='Bible verse reference')
    
    # Button 1
    button1_text = models.CharField(max_length=100, default='Books', help_text='Text for first button')
    button1_url = models.CharField(max_length=200, default='#', help_text='URL for first button')
    
    # Button 2
    button2_text = models.CharField(max_length=100, default='School of Ministry', 
                                   help_text='Text for second button')
    button2_url = models.CharField(max_length=200, default='/school-of-ministry/', 
                                  help_text='URL for second button')
    
    # Button 3
    button3_text = models.CharField(max_length=100, default='Partner With Us', 
                                   help_text='Text for third button')
    button3_url = models.CharField(max_length=200, default='/donate/', 
                                  help_text='URL for third button')
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CTA Card'
        verbose_name_plural = 'CTA Card'

    def __str__(self):
        return "Call-to-Action Card"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class MensMinistry(models.Model):
    """Single section for Men's Ministry on the homepage"""
    title = models.CharField(max_length=200, default="Men's Ministry")
    video_url = models.URLField(
        help_text="YouTube embed URL for the Men's Ministry video (e.g. https://www.youtube.com/embed/VIDEO_ID)",
    )
    description = models.TextField(help_text="Text shown next to the video")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Men's Ministry"
        verbose_name_plural = "Men's Ministry"

    def __str__(self):
        return self.title

    def get_embed_url(self):
        """Return a YouTube embed URL if possible, or the raw URL as fallback."""
        return _to_youtube_embed(self.video_url)


class Partner(models.Model):
    """Logo strip for ministry partners on the homepage"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/', help_text='Logo image shown in the partners carousel')
    use_cropping = models.BooleanField(default=False, help_text='Check this box to enable cropping. When unchecked, the original image will be used as-is.')
    logo_cropping = ImageRatioField('logo', '300x200', size_warning=True, help_text='Crop the logo to your desired size (only used if "Use Cropping" is checked)')
    website_url = models.URLField(blank=True, help_text='Optional link to open when the logo is clicked')
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'
        indexes = [
            models.Index(fields=['is_active', 'display_order']),
        ]

    def __str__(self):
        return self.name


class NewsletterSubscriber(models.Model):
    """Email addresses collected from the footer newsletter form."""
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text='Uncheck to stop sending newsletters to this address')

    class Meta:
        ordering = ['-date_subscribed']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

    def __str__(self):
        return self.email


class SchoolMinistryEnrollment(models.Model):
    """People who enroll to join the School of Ministry programme."""
    programme = models.CharField(
        max_length=100,
        default='School of Ministry',
        help_text='Programme name (kept for reporting/future expansion)',
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enrolled_at']
        verbose_name = 'School Ministry Enrollment'
        verbose_name_plural = 'School Ministry Enrollments'

    def __str__(self):
        return f"{self.name} <{self.email}>"


class SidebarPromo(models.Model):
    """Image or video holder for the sidebar (fills negative space below FAQs / Verse of the Day)"""
    image = models.ImageField(
        upload_to='sidebar_promos/',
        help_text='Image or thumbnail (used as fallback when no video)',
    )
    image_cropping = ImageRatioField(
        'image', '300x400', size_warning=True,
        help_text='Crop to portrait 3:4. Images display as portrait in the sidebar.',
    )
    video_url = models.URLField(
        blank=True,
        help_text='Optional video URL (e.g. YouTube embed). If set, video is shown instead of image.',
    )
    caption = models.CharField(max_length=200, blank=True, help_text='Optional caption below the media')
    link_url = models.URLField(
        blank=True,
        help_text='Optional link when image/video is clicked',
    )
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = 'Sidebar Promo'
        verbose_name_plural = 'Sidebar Promos'
        indexes = [
            models.Index(fields=['is_active', 'display_order']),
        ]

    def __str__(self):
        return self.caption or f'Sidebar Promo #{self.id}'

    def get_embed_url(self):
        """Return YouTube embed URL if possible, or empty string."""
        return _to_youtube_embed(self.video_url)


class FAQ(models.Model):
    """Model for Frequently Asked Questions displayed in the sidebar"""
    question = models.CharField(max_length=500, help_text='The question text')
    answer = models.TextField(help_text='The answer text (supports HTML)')
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first')
    is_active = models.BooleanField(default=True, help_text='Show this FAQ in the sidebar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'question']
        verbose_name = 'Common Question'
        verbose_name_plural = 'Common Questions'
        indexes = [
            models.Index(fields=['is_active', 'display_order']),
        ]

    def __str__(self):
        return self.question[:50] + ('...' if len(self.question) > 50 else '')


class PageView(models.Model):
    """Tracks page views for analytics: visits per month, unique visitors (by IP), and most-read articles."""
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=500, db_index=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Visitor IP for unique visit tracking (one visit per IP per day)',
    )
    content_type = models.CharField(max_length=50, null=True, blank=True, db_index=True,
        help_text='Model name for article views: wordoftruth, childrensbread, news')
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True,
        help_text='PK of the article for most-read stats')

    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-viewed_at']),
            models.Index(fields=['ip_address', '-viewed_at']),
        ]


def _youtube_video_id(raw_url: str) -> str:
    """Extract YouTube video ID from watch, youtu.be, shorts, or embed URL. Returns empty string if not a YouTube URL."""
    if not raw_url:
        return ''
    try:
        parsed = urlparse(raw_url)
        host = parsed.netloc.lower()
        video_id = ''
        if 'youtube.com' in host and parsed.path.startswith('/embed/'):
            video_id = (parsed.path.rstrip('/').split('/embed/')[-1].split('/')[0] or '').split('?')[0]
        elif host == 'youtu.be':
            video_id = ((parsed.path or '').lstrip('/').split('/')[0] or '').split('?')[0]
        elif 'youtube.com' in host and parsed.path == '/watch':
            qs = parse_qs(parsed.query)
            video_id = (qs.get('v', ['']) or [''])[0] or ''
        elif 'youtube.com' in host and parsed.path.startswith('/shorts/'):
            video_id = (parsed.path.split('/shorts/', 1)[-1].split('/')[0] or '').split('?')[0]
        return (video_id or '').strip()
    except Exception:
        pass
    return ''


def _to_youtube_embed(raw_url: str) -> str:
    """
    Convert common YouTube URLs (watch, youtu.be, shorts) to an embeddable URL.
    If it can't be parsed, return the original.
    """
    if not raw_url:
        return ''
    video_id = _youtube_video_id(raw_url)
    if video_id:
        return f'https://www.youtube.com/embed/{video_id}'
    try:
        parsed = urlparse(raw_url)
        if 'youtube.com' in parsed.netloc.lower() and parsed.path.startswith('/embed/'):
            return raw_url
    except Exception:
        pass
    return raw_url
