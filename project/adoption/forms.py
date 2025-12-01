from django import forms
from .models import AdoptionRequest, AdoptionPost
from pets.models import PetProfile


class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = [
            'full_name', 'email', 'phone_number', 'address',
            'housing_type', 'owns_or_rents', 'has_yard', 'landlord_approval',
            'has_pets_currently', 'current_pets_description', 'previous_pet_experience',
            'why_adopt', 'daily_care_plan',
            'veterinarian_info', 'references', 'additional_notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com',
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': '(555) 123-4567',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Enter your full address',
                'rows': 3,
                'class': 'form-control'
            }),
            'housing_type': forms.TextInput(attrs={
                'placeholder': 'e.g., House, Apartment, Condo',
                'class': 'form-control'
            }),
            'owns_or_rents': forms.Select(attrs={'class': 'form-control'}),
            'current_pets_description': forms.Textarea(attrs={
                'placeholder': 'Describe your current pets (if any)',
                'rows': 3,
                'class': 'form-control'
            }),
            'previous_pet_experience': forms.Textarea(attrs={
                'placeholder': 'Tell us about your experience with pets',
                'rows': 4,
                'class': 'form-control'
            }),
            'why_adopt': forms.Textarea(attrs={
                'placeholder': 'Why do you want to adopt this pet?',
                'rows': 4,
                'class': 'form-control'
            }),
            'daily_care_plan': forms.Textarea(attrs={
                'placeholder': 'How will you care for this pet on a daily basis?',
                'rows': 4,
                'class': 'form-control'
            }),
            'veterinarian_info': forms.Textarea(attrs={
                'placeholder': 'Your veterinarian\'s name and contact information (optional)',
                'rows': 3,
                'class': 'form-control'
            }),
            'references': forms.Textarea(attrs={
                'placeholder': 'Names and contact information of personal references (optional)',
                'rows': 3,
                'class': 'form-control'
            }),
            'additional_notes': forms.Textarea(attrs={
                'placeholder': 'Any additional information you\'d like to share',
                'rows': 3,
                'class': 'form-control'
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'address': 'Home Address',
            'housing_type': 'Type of Housing',
            'owns_or_rents': 'Do you own or rent?',
            'has_yard': 'Do you have a yard?',
            'landlord_approval': 'Do you have landlord approval for pets? (if renting)',
            'has_pets_currently': 'Do you currently have pets?',
            'current_pets_description': 'Current Pets',
            'previous_pet_experience': 'Previous Pet Experience',
            'why_adopt': 'Why do you want to adopt this pet?',
            'daily_care_plan': 'Daily Care Plan',
            'veterinarian_info': 'Veterinarian Information',
            'references': 'Personal References',
            'additional_notes': 'Additional Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill with user information if available
        if 'initial' in kwargs and 'user' in kwargs['initial']:
            user = kwargs['initial']['user']
            if user.is_authenticated:
                self.fields['full_name'].initial = user.profile_name or user.username
                self.fields['email'].initial = user.email
                self.fields['phone_number'].initial = user.phone_number or ''


class AdoptionPostForm(forms.ModelForm):
    class Meta:
        model = AdoptionPost
        fields = ['pet', 'requirements', 'additional_info']
        widgets = {
            'requirements': forms.Textarea(attrs={
                'placeholder': 'Describe any specific requirements for potential adopters...',
                'rows': 4,
                'class': 'form-control'
            }),
            'additional_info': forms.Textarea(attrs={
                'placeholder': 'Any additional information about the adoption...',
                'rows': 4,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter pets to show only those owned by the current user
        if user:
            self.fields['pet'].queryset = PetProfile.objects.filter(owner=user)
            self.fields['pet'].empty_label = "Select one of your pets"
