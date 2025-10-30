from django import forms
from .models import PetProfile, PetTrait

class PetProfileForm(forms.ModelForm):
    # Define common personality traits as choices
    TRAIT_CHOICES = [
        ('Friendly', 'Friendly'),
        ('Energetic', 'Energetic'),
        ('Calm', 'Calm'),
        ('Social', 'Social'),
        ('Independent', 'Independent'),
        ('Playful', 'Playful'),
        ('Gentle', 'Gentle'),
        ('Protective', 'Protective'),
        ('Curious', 'Curious'),
        ('Affectionate', 'Affectionate'),
        ('Shy', 'Shy'),
        ('Confident', 'Confident'),
    ]

    traits = forms.MultipleChoiceField(
        choices=TRAIT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Personality Traits'
    )

    class Meta:
        model = PetProfile
        fields = [
            'name', 'species', 'breed', 'age', 'general_size', 'energy_level',
            'weight', 'color_markings', 'bio', 'profile_picture',
            'is_playdate_available', 'privacy_settings'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Buddy'}),
            'breed': forms.TextInput(attrs={'placeholder': 'e.g., Golden Retriever'}),
            'age': forms.TextInput(attrs={'placeholder': 'e.g., 3 years'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'e.g., 65', 'step': '0.01'}),
            'color_markings': forms.TextInput(attrs={'placeholder': 'e.g., Golden with white chest'}),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell us about your pet\'s personality, habits, and what makes them special...',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing an existing pet, pre-populate the traits
        if self.instance and self.instance.pk:
            existing_traits = self.instance.traits.values_list('trait', flat=True)
            self.initial['traits'] = list(existing_traits)

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if commit:
            # Clear existing traits
            instance.traits.all().delete()

            # Add selected traits
            selected_traits = self.cleaned_data.get('traits', [])
            for trait_name in selected_traits:
                PetTrait.objects.create(pet=instance, trait=trait_name)

        return instance
