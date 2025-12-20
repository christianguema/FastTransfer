from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.template.context_processors import request
from userauths.forms import UserRegisterForm
from userauths.models import User


def register_views(request):
    if(request.method == "POST"):
        form = UserRegisterForm(request.POST or None)
        if(form.is_valid()):
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request,f'{username}, Votre compte à été créer avec succès')
            new_user = authenticate(username=form.cleaned_data["email"], password=form.cleaned_data["password1"])
            login(request, new_user)
            return HttpResponse(request,'Utlisateur connecté')
    else:
        form = UserRegisterForm()
        print("User can not be registered")
    
    context = {
        "form":form
    }

    return render(request,'auth/register.html', context)


def login_view(request):
    if (request.user.is_authenticated):
        messages.warning(request,f"Vous etes deja connecté")
        return HttpResponse(request,'Vous etes deja connecté')
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("Email:", email)
        print("Password:", password)

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Vous etes connecté")
                return HttpResponse(request,"Vous etes connecté")
            else:
                messages.warning(request,"L'utilisateur n'exit pas, Veuillez créer un compte.")
        except:
            messages.warning(request, f"L'utilisateur avec l'email: {email} n'exist pas.")
        
       
    return render(request, 'auth/login.html')


def logout_view(request, peanout):
    logout(request)
    messages.success(request, "Vous etes déconnecté")
    return HttpResponse(request,"vous etes deconnecté")