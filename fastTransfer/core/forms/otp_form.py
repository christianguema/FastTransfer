from django import forms
from userauths.models import OTP


class OTPVerificationForm(forms.Form):
    """Formulaire de vérification OTP"""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border-2 border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white py-3 px-4 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 dark:focus:ring-brand-900 transition text-center font-bold text-2xl',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'autocomplete': 'off'
        }),
        label='Code OTP',
        help_text='Entrez le code à 6 chiffres envoyé à votre email'
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        
        # Vérifier que le code ne contient que des chiffres
        if not code.isdigit():
            raise forms.ValidationError("Le code OTP doit contenir uniquement des chiffres.")
        
        # Vérifier que le code a exactement 6 chiffres
        if len(code) != 6:
            raise forms.ValidationError("Le code OTP doit avoir exactement 6 chiffres.")
        
        return code
