# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ChurchAboutpage(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255)
    image = models.CharField(max_length=100, blank=True, null=True)
    image_cropping = models.CharField(max_length=255)
    body = models.TextField()
    updated_at = models.DateTimeField()
    video_url = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'church_aboutpage'


class ChurchBook(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.CharField(max_length=100)
    image_cropping = models.CharField(max_length=255)
    description = models.TextField()
    review = models.TextField()
    whatsapp_number = models.CharField(max_length=20)
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_book'


class ChurchCalendarevent(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    event_type = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    event_date = models.DateField()
    updated_at = models.DateTimeField()
    image = models.CharField(max_length=100, blank=True, null=True)
    image_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_calendarevent'


class ChurchChildrensbread(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    summary = models.TextField()
    author_name = models.CharField(max_length=100)
    image = models.CharField(max_length=100, blank=True, null=True)
    image_cropping = models.CharField(max_length=255)
    body = models.TextField()
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_childrensbread'


class ChurchContactmessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField()
    is_read = models.BooleanField()
    phone = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'church_contactmessage'


class ChurchCtacard(models.Model):
    id = models.BigAutoField(primary_key=True)
    quote_text = models.TextField()
    verse_reference = models.CharField(max_length=50)
    button1_text = models.CharField(max_length=100)
    button1_url = models.CharField(max_length=200)
    button2_text = models.CharField(max_length=100)
    button2_url = models.CharField(max_length=200)
    button3_text = models.CharField(max_length=100)
    button3_url = models.CharField(max_length=200)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_ctacard'


class ChurchFaq(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    display_order = models.IntegerField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_faq'


class ChurchGalleryimage(models.Model):
    id = models.BigAutoField(primary_key=True)
    caption = models.CharField(max_length=200)
    image = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField()
    duration_label = models.CharField(max_length=10)
    video_url = models.CharField(max_length=200)
    image_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_galleryimage'


class ChurchHerosettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.CharField(max_length=100)
    updated_at = models.DateTimeField()
    image_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_herosettings'


class ChurchInfocard(models.Model):
    id = models.BigAutoField(primary_key=True)
    card_type = models.CharField(unique=True, max_length=20)
    title = models.CharField(max_length=200)
    image = models.CharField(max_length=100)
    headline = models.CharField(max_length=200)
    summary = models.TextField()
    author_name = models.CharField(max_length=100)
    link_url = models.CharField(max_length=200)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    content = models.TextField()
    slug = models.CharField(unique=True, max_length=200)
    image_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_infocard'


class ChurchMantalk(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    summary = models.TextField()
    author_name = models.CharField(max_length=100)
    image = models.CharField(max_length=100, blank=True, null=True)
    image_cropping = models.CharField(max_length=255)
    body = models.TextField()
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_mantalk'


class ChurchMensministry(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    video_url = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_mensministry'


class ChurchNewsitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    image = models.CharField(max_length=100)
    summary = models.TextField()
    body = models.TextField()
    event_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    is_published = models.BooleanField()
    image_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_newsitem'


class ChurchNewslettersubscriber(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=254)
    date_subscribed = models.DateTimeField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'church_newslettersubscriber'


class ChurchNewsline(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    image = models.CharField(max_length=100)
    image_cropping = models.CharField(max_length=255)
    video_url = models.CharField(max_length=200)
    summary = models.TextField()
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'church_newsline'


class ChurchPageview(models.Model):
    id = models.BigAutoField(primary_key=True)
    viewed_at = models.DateTimeField()
    path = models.CharField(max_length=500)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'church_pageview'


class ChurchPartner(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    logo = models.CharField(max_length=100)
    website_url = models.CharField(max_length=200)
    display_order = models.IntegerField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    logo_cropping = models.CharField(max_length=255)
    use_cropping = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'church_partner'


class ChurchPartnerinquiry(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=254)
    message = models.TextField()
    created_at = models.DateTimeField()
    is_read = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'church_partnerinquiry'


class ChurchSchoolministryenrollment(models.Model):
    id = models.BigAutoField(primary_key=True)
    programme = models.CharField(max_length=100)
    name = models.CharField(max_length=120)
    email = models.CharField(unique=True, max_length=254)
    phone_number = models.CharField(max_length=30)
    enrolled_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_schoolministryenrollment'


class ChurchSidebarpromo(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.CharField(max_length=100)
    image_cropping = models.CharField(max_length=255)
    video_url = models.CharField(max_length=200)
    caption = models.CharField(max_length=200)
    link_url = models.CharField(max_length=200)
    display_order = models.IntegerField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'church_sidebarpromo'


class ChurchTestimonial(models.Model):
    id = models.BigAutoField(primary_key=True)
    member_name = models.CharField(max_length=100)
    photo = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField()
    approved = models.BooleanField()
    created_at = models.DateTimeField()
    video_url = models.CharField(max_length=200)
    photo_cropping = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'church_testimonial'


class ChurchVerse(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    reference = models.CharField(max_length=200)
    date_posted = models.DateTimeField()
    is_active = models.BooleanField()
    is_featured = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'church_verse'


class ChurchWordoftruth(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    summary = models.TextField()
    is_published = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    image = models.CharField(max_length=100, blank=True, null=True)
    image_cropping = models.CharField(max_length=255)
    body = models.TextField()
    author_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'church_wordoftruth'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EasyThumbnailsSource(models.Model):
    storage_hash = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'easy_thumbnails_source'
        unique_together = (('storage_hash', 'name'),)


class EasyThumbnailsThumbnail(models.Model):
    storage_hash = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    modified = models.DateTimeField()
    source = models.ForeignKey(EasyThumbnailsSource, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'easy_thumbnails_thumbnail'
        unique_together = (('storage_hash', 'name', 'source'),)


class EasyThumbnailsThumbnaildimensions(models.Model):
    thumbnail = models.OneToOneField(EasyThumbnailsThumbnail, models.DO_NOTHING)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'easy_thumbnails_thumbnaildimensions'
