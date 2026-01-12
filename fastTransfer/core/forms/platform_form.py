from django import forms
from core.models import Platform

class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ['name', 'withdrawal_fee_rate']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': Platform.objects.first().name if Platform.objects.exists() else 'Nom de la plateforme',
                'class': 'dark:bg-dark-900 shadow-theme-xs focus:border-brand-300 focus:ring-brand-500/10 dark:focus:border-brand-800 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:ring-3 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30'}),
            
            'withdrawal_fee_rate': forms.NumberInput(attrs={
                'placeholder': Platform.objects.first().withdrawal_fee_rate if Platform.objects.exists() else 'Taux de frais de retrait (%)',
                'class': 'dark:bg-dark-900 shadow-theme-xs focus:border-brand-300 focus:ring-brand-500/10 dark:focus:border-brand-800 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:ring-3 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30'}),
        }