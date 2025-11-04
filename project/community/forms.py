from django import forms
from .models import CommunityAlert, Post, Comment


class CommunityAlertForm(forms.ModelForm):
    """Form for creating and editing community alerts"""

    class Meta:
        model = CommunityAlert
        fields = [
            'alert_type', 'title', 'description', 'pet_type', 'size',
            'color_markings', 'location', 'latitude', 'longitude',
            'contact_info', 'photo'
        ]
        widgets = {
            'alert_type': forms.RadioSelect(),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Found Black Cat near Park',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Provide detailed description including behavior, distinguishing features, circumstances...',
                'rows': 4
            }),
            'pet_type': forms.TextInput(attrs={
                'placeholder': 'e.g., Dog, Cat'
            }),
            'size': forms.TextInput(attrs={
                'placeholder': 'e.g., Small, Medium, Large'
            }),
            'color_markings': forms.TextInput(attrs={
                'placeholder': 'e.g., Brown with white chest'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Street address or landmark',
                'maxlength': '255'
            }),
            'contact_info': forms.TextInput(attrs={
                'placeholder': 'Phone number or email',
                'maxlength': '100'
            }),
            'photo': forms.FileInput(attrs={
                'accept': 'image/*'
            }),
        }
        labels = {
            'alert_type': 'Alert Type',
            'title': 'Alert Title',
            'description': 'Description',
            'pet_type': 'Pet Type',
            'size': 'Size',
            'color_markings': 'Color/Markings',
            'location': 'Location (where found/last seen)',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'contact_info': 'Contact Information',
            'photo': 'Photos',
        }

    def clean_contact_info(self):
        """Validate that contact_info is not empty"""
        contact_info = self.cleaned_data.get('contact_info')
        if not contact_info or not contact_info.strip():
            raise forms.ValidationError('Contact information is required.')
        return contact_info

    def clean_location(self):
        """Validate that location is not empty"""
        location = self.cleaned_data.get('location')
        if not location or not location.strip():
            raise forms.ValidationError('Location is required.')
        return location


class PostForm(forms.ModelForm):
    """Form for creating community posts"""

    class Meta:
        model = Post
        fields = ['caption', 'photo']
        widgets = {
            'caption': forms.Textarea(attrs={
                'placeholder': "What's happening in your pet community?",
                'rows': 3
            }),
            'photo': forms.FileInput(attrs={
                'accept': 'image/*'
            }),
        }


class CommentForm(forms.ModelForm):
    """Form for posting comments"""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Write a comment...',
                'rows': 2
            }),
        }

    def clean_text(self):
        """Validate that comment text is not empty or whitespace only"""
        text = self.cleaned_data.get('text')
        if not text or not text.strip():
            raise forms.ValidationError('Comment cannot be empty.')
        return text
