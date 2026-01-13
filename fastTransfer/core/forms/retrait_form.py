from django import forms


class widrawForm(forms.Form):
    amount = forms.IntegerField(
        min_value=1,
        label="Montant (Fcfa)",
        widget=forms.NumberInput(attrs={
            "placeholder": "Entrez le montant à rétirer",
            "class": "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        })
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return amount