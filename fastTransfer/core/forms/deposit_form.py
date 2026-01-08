from django import forms


class DepositForm(forms.Form):
    amount = forms.IntegerField(
        min_value=1,
        label="Montant (€)",
        widget=forms.NumberInput(attrs={
            "placeholder": "Entrez le montant à déposer",
            "class": "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        })
    )