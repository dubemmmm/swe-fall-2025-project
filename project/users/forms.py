from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled input field"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'id': 'id_email'
        })


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styled input fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter new password',
            'id': 'id_new_password1'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm new password',
            'id': 'id_new_password2'
        })
