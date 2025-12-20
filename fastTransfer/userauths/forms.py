from django import forms
from userauths.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Requis.',widget=forms.TextInput(attrs={"placeholder":"Nom"}))
    last_name = forms.CharField(max_length=30, required=True, help_text='Requis.',widget=forms.TextInput(attrs={"placeholder":"Prenom"}))
    gender = forms.ChoiceField(choices=[('m', 'M'), ('f', 'F')], required=True, help_text='Requis.')
    phone = forms.CharField(max_length=15, required=True, help_text='Requis.', widget=forms.TextInput(attrs={"placeholder":"Contact"}))
    email = forms.EmailField(max_length=254, required=True, help_text='Requis. Entrez une adresse email valide.',widget=forms.TextInput(attrs={"placeholder":"Email"}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='Requis.')
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, help_text='Requis. Entrez le même mot de passe que précédemment pour vérification.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'phone', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
