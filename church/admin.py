from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.forms import ModelForm
from django.forms.widgets import ColorInput
from image_cropping import ImageCroppingMixin
from .models import Verse, NewsItem, NewsLine, CalendarEvent, Testimonial, GalleryImage, HeroSettings, AboutPage, InfoCard, CTACard, MensMinistry, Partner, NewsletterSubscriber, SchoolMinistryEnrollment, FAQ, SidebarPromo, WordOfTruth, ChildrensBread, PageView, ContactMessage


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ('reference', 'content_preview', 'is_active', 'is_featured', 'date_posted')
    list_filter = ('is_active', 'is_featured', 'date_posted')
    search_fields = ('content', 'reference')
    list_editable = ('is_active', 'is_featured')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(NewsLine)
class NewsLineAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('title', 'is_published', 'has_video', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at')

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Video?'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_published'),
            'description': 'Articles and videos shown on the News Line page.',
        }),
        ('Media', {
            'fields': ('image', 'image_cropping', 'video_url'),
            'description': 'Upload a poster image or provide a YouTube video URL. If a video is provided, it will be displayed instead of the poster on the detail view, but the poster is still used as a thumbnail.',
        }),
        ('Content', {
            'fields': ('summary',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NewsItem)
class NewsItemAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('title', 'is_published', 'event_date', 'created_at', 'view_listing_link')
    list_filter = ('is_published', 'event_date', 'created_at')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)
    readonly_fields = ('created_at',)

    def view_listing_link(self, obj):
        url = reverse('news_line_list')
        return format_html('<a href="{}" target="_blank" rel="noopener">View listing</a>', url)
    view_listing_link.short_description = 'News Line'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_published'),
            'description': 'Articles shown on the News Line listing page (linked from the hero section).',
        }),
        ('Content', {
            'fields': ('image', 'image_cropping', 'summary', 'body')
        }),
        ('Event Details', {
            'fields': ('event_date',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class CalendarEventForm(ModelForm):
    """Custom form with color picker widget"""
    class Meta:
        model = CalendarEvent
        fields = '__all__'
        widgets = {
            'color': ColorInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; cursor: pointer;'}),
        }


@admin.register(CalendarEvent)
class CalendarEventAdmin(ImageCroppingMixin, admin.ModelAdmin):
    form = CalendarEventForm
    list_display = ('title', 'event_date', 'event_type', 'calendar_link', 'is_published')
    list_filter = ('event_type', 'is_published', 'event_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'event_date'
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at', 'calendar_preview', 'color_preview')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_date', 'event_type')
        }),
        ('Details', {
            'fields': ('location', 'image', 'image_cropping', 'color', 'color_preview'),
            'description': 'Select a color for the event label. Click the color box to open the color picker. Use the image cropper to crop the image.'
        }),
        ('Calendar Preview', {
            'fields': ('calendar_preview',),
            'description': 'View this event on the calendar page'
        }),
        ('Status', {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
    )
    
    def calendar_link(self, obj):
        if obj.id:
            url = reverse('news_list') + f'?year={obj.event_date.year}&month={obj.event_date.month}'
            return format_html('<a href="{}" target="_blank">View on Calendar</a>', url)
        return '-'
    calendar_link.short_description = 'Calendar'
    
    def calendar_preview(self, obj):
        if obj.id:
            url = reverse('news_list') + f'?year={obj.event_date.year}&month={obj.event_date.month}'
            return format_html(
                '<div style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin: 10px 0;">'
                '<p><strong>View on Calendar:</strong></p>'
                '<iframe src="{}" style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px;"></iframe>'
                '</div>',
                url
            )
        return 'Save the event first to see calendar preview'
    calendar_preview.short_description = 'Calendar Preview'
    
    def color_preview(self, obj):
        """Show a preview of the selected color"""
        if obj.id:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">'
                '<div style="width: 60px; height: 60px; background-color: {}; border: 2px solid #ddd; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>'
                '<div>'
                '<p style="margin: 0; font-weight: bold;">Color Preview</p>'
                '<p style="margin: 0; color: #666; font-size: 12px;">Code: {}</p>'
                '</div>'
                '</div>',
                obj.color, obj.color
            )
        return 'Select a color and save to see preview'
    color_preview.short_description = 'Color Preview'
    color_preview.readonly = True


@admin.register(Testimonial)
class TestimonialAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('member_name', 'approved', 'text_preview', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('member_name', 'text')
    list_editable = ('approved',)
    fieldsets = (
        (None, {
            'fields': ('member_name', 'approved')
        }),
        ('Media', {
            'fields': ('video_url', 'photo', 'photo_cropping'),
            'description': 'Provide either a video URL or an image (or both). Use the image cropper to crop the photo.',
        }),
        ('Content', {
            'fields': ('text',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(GalleryImage)
class GalleryImageAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('caption', 'category', 'has_video', 'uploaded_at')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('caption', 'category', 'video_url')
    fieldsets = (
        (None, {
            'fields': ('caption', 'category')
        }),
        ('Media', {
            'fields': ('image', 'image_cropping', 'video_url', 'duration_label'),
            'description': 'Provide an image for all items. Add a video URL for video entries (e.g. YouTube embed URL). Use the image cropper to crop the image.',
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('uploaded_at',)

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Video?'


@admin.register(HeroSettings)
class HeroSettingsAdmin(ImageCroppingMixin, admin.ModelAdmin):
    fields = ('image', 'image_cropping', 'updated_at')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not HeroSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False


@admin.register(AboutPage)
class AboutPageAdmin(ImageCroppingMixin, admin.ModelAdmin):
    fields = ('title', 'subtitle', 'image', 'image_cropping', 'video_url', 'body', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Only allow one instance
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False


@admin.register(InfoCard)
class InfoCardAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('card_type', 'title', 'headline', 'listing_link', 'is_active', 'updated_at')
    list_filter = ('card_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'headline', 'summary', 'author_name')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')

    class Media:
        css = {'all': ()}
        js = ()

    def listing_link(self, obj):
        """Link to the article listing page this card leads to."""
        if not obj:
            return '-'
        from django.urls import reverse
        if obj.card_type == 'childrens_bread':
            url = reverse('childrens_bread_list')
            label = 'Children\'s Bread'
        elif obj.card_type == 'word_of_truth':
            url = reverse('word_of_truth_list')
            label = 'Word of Truth'
        elif obj.card_type == 'news':
            url = reverse('news_line_list')
            label = 'News Line'
        else:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">View {} listing</a>', url, label)
    listing_link.short_description = 'Listing page'

    fieldsets = (
        ('Card Information', {
            'fields': ('card_type', 'title', 'slug', 'is_active'),
            'description': 'Hero section card shown on the homepage. Each card links to its article listing (Children\'s Bread, Word of Truth, or News Line). Edit those articles under Church in the sidebar.',
        }),
        ('Content', {
            'fields': ('image', 'image_cropping', 'headline', 'summary', 'content', 'author_name'),
            'description': 'Image, headline and summary shown on the hero card. Use the image cropper for 16:9 (1600x900) for best display.',
        }),
        ('Link override', {
            'fields': ('link_url',),
            'description': 'Leave blank so the card links to the article listing page (Children\'s Bread, Word of Truth, or News Line). Set a URL here only to override that default.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CTACard)
class CTACardAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not CTACard.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False

    fieldsets = (
        ('Quote Section', {
            'fields': ('quote_text', 'verse_reference')
        }),
        ('Button 1', {
            'fields': ('button1_text', 'button1_url')
        }),
        ('Button 2', {
            'fields': ('button2_text', 'button2_url')
        }),
        ('Button 3', {
            'fields': ('button3_text', 'button3_url')
        }),
    )


@admin.register(MensMinistry)
class MensMinistryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)


@admin.register(Partner)
class PartnerAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active', 'use_cropping', 'display_order', 'created_at')
    list_filter = ('is_active', 'use_cropping', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    fields = ('name', 'logo', 'use_cropping', 'logo_cropping', 'website_url', 'display_order', 'is_active', 'created_at')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'date_subscribed')
    list_filter = ('is_active', 'date_subscribed')
    search_fields = ('email',)


@admin.register(SchoolMinistryEnrollment)
class SchoolMinistryEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'programme', 'enrolled_at')
    list_filter = ('programme', 'enrolled_at')
    search_fields = ('name', 'email', 'phone_number')
    readonly_fields = ('enrolled_at',)


@admin.register(SidebarPromo)
class SidebarPromoAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('caption_preview', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('caption',)
    list_editable = ('display_order', 'is_active')
    fields = (
        'image', 'image_cropping', 'video_url', 'caption', 'link_url',
        'display_order', 'is_active', 'created_at',
    )
    readonly_fields = ('created_at',)

    def caption_preview(self, obj):
        return obj.caption or f'Promo #{obj.id}'
    caption_preview.short_description = 'Caption'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('display_order', 'is_active')
    fieldsets = (
        ('Question & Answer', {
            'fields': ('question', 'answer')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def question_preview(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_preview.short_description = 'Question'


@admin.register(WordOfTruth)
class WordOfTruthAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('title', 'author_name', 'is_published', 'created_at', 'view_listing_link')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'summary', 'author_name', 'body')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def view_listing_link(self, obj):
        url = reverse('word_of_truth_list')
        return format_html('<a href="{}" target="_blank" rel="noopener">View listing</a>', url)
    view_listing_link.short_description = 'Listing'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_published'),
            'description': 'Articles shown on the Word of Truth listing page (linked from the hero section).',
        }),
        ('Content & Media', {
            'fields': ('author_name', 'image', 'image_cropping', 'summary', 'body'),
            'description': 'Images are cropped to 800x600 for consistency.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChildrensBread)
class ChildrensBreadAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('title', 'author_name', 'is_published', 'created_at', 'view_listing_link')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'summary', 'author_name', 'body')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def view_listing_link(self, obj):
        url = reverse('childrens_bread_list')
        return format_html('<a href="{}" target="_blank" rel="noopener">View listing</a>', url)
    view_listing_link.short_description = 'Listing'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_published'),
            'description': 'Articles shown on the Children\'s Bread listing page (linked from the hero section).',
        }),
        ('Content & Media', {
            'fields': ('author_name', 'image', 'image_cropping', 'summary', 'body'),
            'description': 'Images are cropped to 800x600 for consistency.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('viewed_at', 'ip_address', 'path', 'content_type')
    list_filter = ('viewed_at', 'content_type')
    search_fields = ('ip_address', 'path')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Disable manual creation - messages come from the form
        return False
