from django import forms
from userauths.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Requis.',
        widget=forms.TextInput(attrs={
            "placeholder": "Prénom",
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        })
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return first_name.capitalize()
    
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Requis.',
        widget=forms.TextInput(attrs={
            "placeholder": "Nom",
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        })
    )

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return last_name.capitalize()
    
    gender = forms.ChoiceField(
        choices=[('m', 'Homme'), ('f', 'Femme')], 
        required=True, 
        help_text='Requis.',
        widget=forms.Select(attrs={
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        })
    )

    phone = forms.CharField(
        max_length=15, 
        required=True, 
        help_text='Requis.',
        widget=forms.TextInput(attrs={
            "placeholder": "Contact",
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return phone
    
    
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text='Requis. Entrez une adresse email valide.',
        widget=forms.TextInput(attrs={
            "placeholder": "Email",
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        })
    )
    password1 = forms.CharField(
        label='Mot de passe', 
        widget=forms.PasswordInput(attrs={
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        }), 
        required=True,
        help_text='Requis.'
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe', 
        widget=forms.PasswordInput(attrs={
            "class": "w-full text-blue-900 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-900"
        }),
        required=True,
        help_text='Requis. Entrez le même mot de passe que précédemment pour vérification.'
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'phone', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.gender = self.cleaned_data['gender']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user