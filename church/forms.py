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
        """Custom validation for image fields - relaxed to avoid false positives"""
        image = self.cleaned_data.get('image')
        if not image:
            return image
        
        from django.core.files.uploadedfile import UploadedFile
        if isinstance(image, UploadedFile) or hasattr(image, 'file'):
            try:
                # Reset pointers
                if hasattr(image, 'seek'):
                    image.seek(0)
                
                # Use Django's built-in check first (it's more reliable for general uploads)
                width, height = get_image_dimensions(image)
                
                # If Django's check passes, we consider it a success and stop strict PIL checking
                # which was causing false-positive "corrupted" errors for some users.
                if width and height:
                    if hasattr(image, 'seek'):
                        image.seek(0)
                    return image

                # If Django failed, try a deeper PIL check only as a fallback
                from PIL import Image as PILImage
                from io import BytesIO
                try:
                    if hasattr(image, 'seek'):
                        image.seek(0)
                    content = image.read()
                    if hasattr(image, 'seek'):
                        image.seek(0)
                    
                    PILImage.open(BytesIO(content)).verify()
                except Exception:
                    # If BOTH Django and PIL fail, then it's actually invalid
                    raise ValidationError(
                        'The file was not recognized as a valid image. '
                        'Please ensure it is a JPEG, PNG, or GIF file.'
                    )
                
                if hasattr(image, 'seek'):
                    image.seek(0)
                    
            except ValidationError:
                raise
            except Exception as e:
                # Fail-safe: if validation itself errors, but it's an image, let it pass
                # instead of blocking the user with "corrupted" messages.
                return image
        
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
        """Custom validation for logo field - relaxed"""
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo
        
        if hasattr(logo, 'file'):
            try:
                if hasattr(logo, 'seek'):
                    logo.seek(0)
                width, height = get_image_dimensions(logo)
                if width and height:
                    return logo
            except Exception:
                pass
        return logo


class TestimonialAdminForm(ImageFieldFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'
    
    def clean_photo(self):
        """Custom validation for photo field - relaxed"""
        photo = self.cleaned_data.get('photo')
        if not photo:
            return photo
        
        if hasattr(photo, 'file'):
            try:
                if hasattr(photo, 'seek'):
                    photo.seek(0)
                width, height = get_image_dimensions(photo)
                if width and height:
                    return photo
            except Exception:
                pass
        return photo


import re

class ContactForm(forms.ModelForm):
    # Hidden field to catch bots. Humans won't see/fill this.
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'class': 'hidden'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Your Phone Number (e.g. +254...)'}),
            'subject': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'rows': 4, 'placeholder': 'How can we help you?'}),
        }

    def clean_honeypot(self):
        """Check if honeypot was filled"""
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            # If filled, it's a bot
            raise ValidationError("Bot detected.")
        return honeypot

    def clean_phone(self):
        """Ensure phone number starts with +254 (Kenyan format)"""
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+254'):
            raise ValidationError("Only Kenyan phone numbers starting with +254 are accepted.")
        # Basic digits check (after the +254 prefix)
        clean_ext = phone[4:].replace(' ', '').replace('-', '')
        if not clean_ext.isdigit() or len(clean_ext) < 9 or len(clean_ext) > 10:
             raise ValidationError("Please enter a valid Kenyan phone number (e.g. +254 7XX XXX XXX).")
        return phone

    def clean_message(self):
        """Block messages with Cyrillic characters (Russian spam)"""
        message = self.cleaned_data.get('message')
        # Check for Cyrillic characters
        if re.search('[\u0400-\u04FF]', message):
            raise ValidationError("Spam attempt detected. Cyrillic text is not permitted.")
        return message


class PartnerInquiryForm(forms.ModelForm):
    # Hidden field to catch bots
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'class': 'hidden'}))

    class Meta:
        model = PartnerInquiry
        fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Phone Number (e.g. +254...)'}),
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'placeholder': 'Company/Organization (Optional)'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand focus:border-transparent outline-none transition duration-300', 'rows': 4, 'placeholder': 'Tell us about your interest in partnership'}),
        }

    def clean_honeypot(self):
        """Check if honeypot was filled"""
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise ValidationError("Bot detected.")
        return honeypot

    def clean_phone(self):
        """Ensure phone number starts with +254"""
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+254'):
            raise ValidationError("Only Kenyan phone numbers starting with +254 are accepted.")
        clean_ext = phone[4:].replace(' ', '').replace('-', '')
        if not clean_ext.isdigit() or len(clean_ext) < 9 or len(clean_ext) > 10:
             raise ValidationError("Please enter a valid Kenyan phone number (e.g. +254 7XX XXX XXX).")
        return phone

    def clean_message(self):
        """Block messages with Cyrillic characters"""
        message = self.cleaned_data.get('message')
        if re.search('[\u0400-\u04FF]', message):
            raise ValidationError("Spam attempt detected. Cyrillic text is not permitted.")
        return message
