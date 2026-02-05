"""
Management command to regenerate all thumbnails and upload to GCS.
Run this on Cloud Run or locally with GCS credentials.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from church.models import GalleryImage, SidebarPromo, HeroSettings, CTACard, Testimonial, Partner
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Regenerate all thumbnails for GalleryImage, SidebarPromo, and other image models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be regenerated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No thumbnails will be generated'))
        
        self.stdout.write(f'THUMBNAIL_DEFAULT_STORAGE: {getattr(settings, "THUMBNAIL_DEFAULT_STORAGE", "Not set")}')
        self.stdout.write(f'DEFAULT_FILE_STORAGE: {getattr(settings, "DEFAULT_FILE_STORAGE", "Not set")}')
        self.stdout.write(f'GS_BUCKET_NAME: {getattr(settings, "GS_BUCKET_NAME", "Not set")}')
        
        # Thumbnail sizes to generate
        sizes = [
            {'size': (100, 100), 'crop': 'smart'},
            {'size': (200, 150), 'crop': 'detail'},
            {'size': (300, 300), 'crop': 'detail', 'upscale': True},
            {'size': (300, 400), 'crop': True, 'detail': True},
            {'size': (800, 600), 'crop': True, 'detail': True},
        ]
        
        total_generated = 0
        total_errors = 0
        
        # Process GalleryImage
        self.stdout.write('\n--- Processing GalleryImage ---')
        for obj in GalleryImage.objects.all():
            if obj.image and obj.image.name:
                total_generated += self._generate_thumbnails(obj, 'image', 'image_cropping', sizes, dry_run)
        
        # Process SidebarPromo
        self.stdout.write('\n--- Processing SidebarPromo ---')
        try:
            for obj in SidebarPromo.objects.all():
                if obj.image and obj.image.name:
                    total_generated += self._generate_thumbnails(obj, 'image', 'image_cropping', sizes, dry_run)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'SidebarPromo error: {e}'))
        
        # Process HeroSettings
        self.stdout.write('\n--- Processing HeroSettings ---')
        try:
            hero = HeroSettings.objects.first()
            if hero and hero.image and hero.image.name:
                total_generated += self._generate_thumbnails(hero, 'image', 'image_cropping', sizes, dry_run)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'HeroSettings error: {e}'))
        
        # Process CTACard
        self.stdout.write('\n--- Processing CTACard ---')
        try:
            for obj in CTACard.objects.all():
                if hasattr(obj, 'image') and obj.image and obj.image.name:
                    total_generated += self._generate_thumbnails(obj, 'image', 'image_cropping', sizes, dry_run)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'CTACard error: {e}'))
        
        # Process Testimonial
        self.stdout.write('\n--- Processing Testimonial ---')
        try:
            for obj in Testimonial.objects.all():
                if obj.photo and obj.photo.name:
                    total_generated += self._generate_thumbnails(obj, 'photo', 'photo_cropping', sizes, dry_run)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Testimonial error: {e}'))
        
        # Process Partner
        self.stdout.write('\n--- Processing Partner ---')
        try:
            for obj in Partner.objects.all():
                if obj.logo and obj.logo.name:
                    total_generated += self._generate_thumbnails(obj, 'logo', None, sizes, dry_run)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Partner error: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal thumbnails generated: {total_generated}'))
    
    def _generate_thumbnails(self, obj, image_field, crop_field, sizes, dry_run):
        """Generate thumbnails for a single object."""
        count = 0
        image = getattr(obj, image_field, None)
        if not image or not image.name:
            return 0
        
        # Get cropping box if available
        box = None
        if crop_field:
            box = getattr(obj, crop_field, None)
        
        self.stdout.write(f'  Processing: {obj} - {image.name}')
        
        for size_opts in sizes:
            opts = size_opts.copy()
            if box:
                opts['box'] = box
            
            if dry_run:
                self.stdout.write(f'    Would generate: {opts}')
                count += 1
            else:
                try:
                    thumbnailer = get_thumbnailer(image)
                    thumb = thumbnailer.get_thumbnail(opts)
                    self.stdout.write(self.style.SUCCESS(f'    Generated: {thumb.name}'))
                    count += 1
                except InvalidImageFormatError as e:
                    self.stdout.write(self.style.ERROR(f'    Invalid format: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error: {e}'))
        
        return count
