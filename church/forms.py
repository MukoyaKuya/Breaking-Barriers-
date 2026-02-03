"""
Custom forms for admin with improved image validation
"""
from django import forms
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from .models import (
    WordOfTruth, ChildrensBread, ManTalk, NewsLine, NewsItem, InfoCard, 
    GalleryImage, HeroSettings, SidebarPromo, AboutPage, Partner, Testimonial,
    ContactMessage, PartnerInquiry
)


class ImageFieldFormMixin:
    """
    Mixin to add better image validation error handling.
    This helps diagnose issues with image uploads.
    """
    
    def clean_image(self):
        """Custom validation for image fields"""
        image = self.cleaned_data.get('image')
        if not image:
            return image
        
        # Check if it's a new upload (has a file attribute or is an UploadedFile)
        from django.core.files.uploadedfile import UploadedFile
        if isinstance(image, UploadedFile) or hasattr(image, 'file'):
            try:
                # Ensure file pointer is at the beginning
                if hasattr(image, 'seek'):
                    image.seek(0)
                elif hasattr(image, 'file') and hasattr(image.file, 'seek'):
                    image.file.seek(0)
                
                # Try PIL directly first as a test
                from PIL import Image as PILImage
                try:
                    if hasattr(image, 'read'):
                        # Read the file content
                        if hasattr(image, 'seek'):
                            image.seek(0)
                        content = image.read()
                        if hasattr(image, 'seek'):
                            image.seek(0)
                        
                        # Try to open with PIL
                        from io import BytesIO
                        pil_img = PILImage.open(BytesIO(content))
                        pil_img.verify()  # Verify the image
                        pil_img.close()
                    else:
                        # Fall back to Django's validation
                        width, height = get_image_dimensions(image)
                        if width is None or height is None:
                            raise ValidationError(
                                'The file you uploaded was either not an image or a corrupted image. '
                                'Please ensure you are uploading a valid JPEG, PNG, or GIF file.'
                            )
                except PILImage.UnidentifiedImageError:
                    raise ValidationError(
                        'The file you uploaded was not recognized as a valid image format. '
                        'Please upload a JPEG, PNG, or GIF file.'
                    )
                except Exception as pil_error:
                    # If PIL fails, try Django's method
                    try:
                        if hasattr(image, 'seek'):
                            image.seek(0)
                        width, height = get_image_dimensions(image)
                        if width is None or height is None:
                            raise ValidationError(
                                'The file you uploaded was either not an image or a corrupted image. '
                                'Please ensure you are uploading a valid JPEG, PNG, or GIF file.'
                            )
                    except Exception as django_error:
                        error_msg = 'The file you uploaded was either not an image or a corrupted image.'
                        if str(pil_error):
                            error_msg += f' PIL Error: {str(pil_error)}'
                        if str(django_error):
                            error_msg += f' Django Error: {str(django_error)}'
                        raise ValidationError(error_msg)
                
                # Reset file pointer for actual save
                if hasattr(image, 'seek'):
                    image.seek(0)
                elif hasattr(image, 'file') and hasattr(image.file, 'seek'):
                    image.file.seek(0)
                    
            except ValidationError:
                # Re-raise validation errors
                raise
            except Exception as e:
                # Provide more helpful error message
                error_msg = 'The file you uploaded was either not an image or a corrupted image.'
                if str(e):
                    error_msg += f' Error details: {str(e)}'
                raise ValidationError(error_msg)
        
        return image


class WordOfTruthAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = WordOfTruth
        fields = '__all__'


class ChildrensBreadAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = ChildrensBread
        fields = '__all__'


class ManTalkAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = ManTalk
        fields = '__all__'


class NewsLineAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = NewsLine
        fields = '__all__'


class NewsItemAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = '__all__'


class InfoCardAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = InfoCard
        fields = '__all__'


class GalleryImageAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = '__all__'


class HeroSettingsAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = HeroSettings
        fields = '__all__'


class SidebarPromoAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = SidebarPromo
        fields = '__all__'


class AboutPageAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = '__all__'


class PartnerAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = Partner
        fields = '__all__'
    
    def clean_logo(self):
        """Custom validation for logo field"""
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo
        
        # Check if it's a new upload
        if hasattr(logo, 'file'):
            try:
                if hasattr(logo, 'seek'):
                    logo.seek(0)
                
                width, height = get_image_dimensions(logo)
                
                if width is None or height is None:
                    raise ValidationError(
                        'The file you uploaded was either not an image or a corrupted image. '
                        'Please ensure you are uploading a valid JPEG, PNG, or GIF file.'
                    )
                
                if hasattr(logo, 'seek'):
                    logo.seek(0)
                    
            except Exception as e:
                error_msg = 'The file you uploaded was either not an image or a corrupted image.'
                if str(e):
                    error_msg += f' Error details: {str(e)}'
                raise ValidationError(error_msg)
        
        return logo


class TestimonialAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'
    
    def clean_photo(self):
        """Custom validation for photo field"""
        photo = self.cleaned_data.get('photo')
        if not photo:
            return photo
        
        # Check if it's a new upload
        if hasattr(photo, 'file'):
            try:
                if hasattr(photo, 'seek'):
                    photo.seek(0)
                
                width, height = get_image_dimensions(photo)
                
                if width is None or height is None:
                    raise ValidationError(
                        'The file you uploaded was either not an image or a corrupted image. '
                        'Please ensure you are uploading a valid JPEG, PNG, or GIF file.'
                    )
                
                if hasattr(photo, 'seek'):
                    photo.seek(0)
                    
            except Exception as e:
                error_msg = 'The file you uploaded was either not an image or a corrupted image.'
                if str(e):
                    error_msg += f' Error details: {str(e)}'
                raise ValidationError(error_msg)
        
        return photo


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Phone Number'}),
            'subject': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'rows': 4, 'placeholder': 'How can we help you?'}),
        }


class PartnerInquiryForm(forms.ModelForm):
    class Meta:
        model = PartnerInquiry
        fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Phone Number'}),
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Company/Organization (Optional)'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'rows': 4, 'placeholder': 'Tell us about your interest in partnership'}),
        }
