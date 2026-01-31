from django import forms
from .models import ContactMessage, PartnerInquiry
import re


class ContactForm(forms.ModelForm):
    """Form for contact page submissions."""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Your Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Your Email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Your Phone Number',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Subject',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Your Message',
                'rows': 6,
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            raise forms.ValidationError('Phone number is required.')
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
        
        # Check if it contains only digits and optional + at the start
        if not re.match(r'^\+?\d{9,15}$', cleaned):
            raise forms.ValidationError('Please enter a valid phone number (9-15 digits, optional + prefix).')
        
        return phone


class PartnerInquiryForm(forms.ModelForm):
    """Form for partnership inquiries."""
    
    class Meta:
        model = PartnerInquiry
        fields = ['first_name', 'last_name', 'company_name', 'email', 'phone', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Second Name',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Company Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Tel',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-color focus:border-transparent',
                'placeholder': 'Message',
                'rows': 4,
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            raise forms.ValidationError('Phone number is required.')
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
        
        # Check if it contains only digits and optional + at the start
        if not re.match(r'^\+?\d{9,15}$', cleaned):
            raise forms.ValidationError('Please enter a valid phone number.')
        
        return phone
