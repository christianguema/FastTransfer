from django import forms

class TransferForm(forms.Form):
    phone = forms.CharField(
        max_length=30,
        label="Numéro destinataire",
        widget=forms.TextInput(attrs={
            "placeholder": "Numéro du destinataire",
            "class": "dark:bg-dark-900 shadow-theme-xs focus:border-brand-300 focus:ring-brand-500/10 dark:focus:border-brand-800 h-11 w-full rounded-lg border border-gray-300 bg-transparent py-3 pr-4 pl-[84px] text-sm text-gray-800 placeholder:text-gray-400 focus:ring-3 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        })
    )
    amount = forms.IntegerField(
        min_value=1,
        label="Montant (FCFA)",
        widget=forms.NumberInput(attrs={
            "placeholder": "Montant à transférer",
            "class": "dark:bg-dark-900 shadow-theme-xs focus:border-brand-300 focus:ring-brand-500/10 h-11 w-full rounded-lg border border-gray-300 bg-transparent py-3 px-4 text-sm text-gray-800 placeholder:text-gray-400 focus:ring-3 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        })
    )