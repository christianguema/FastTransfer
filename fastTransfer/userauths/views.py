from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
from userauths.forms import UserRegisterForm
from userauths.models import User, OTP
from userauths.utils import generate_otp, otp_expiration
from core.models import VirtualAccount, AccountOwner


def register_views(request):
    if(request.method == "POST"):
        form = UserRegisterForm(request.POST or None)
        if(form.is_valid()):
            new_user = form.save(commit=False)
            new_user.status = "PENDING"
            new_user.save()

            account0wner = AccountOwner.objects.create(
                owner = new_user
            )

            virtual_account = VirtualAccount.objects.create(
                owner=account0wner,
                balance=0,
                is_active=False
            )
            
            #Code d'activation
            otp_code = generate_otp()
            expire_at = otp_expiration()

            otp = OTP.objects.update_or_create(
                defaults={
                    "code":otp_code,
                    "is_expire":False,
                    "expire_at": expire_at
                }
            )

            send_mail(
                subject="Activation de votre compte FastTransfer",
                message=f"""
                    Bonjour {new_user.first_name} {new_user.last_name},

                    Voici votre code d’activation de compte: {otp_code}

                    Ce code expire dans 2 minutes.
                    """,
                from_email=None,
                recipient_list=[new_user.email],
                fail_silently=False
            )

            messages.success(request,"Compte créé. Veuillez vérifier votre email pour l’activation.")

            return redirect('userauths:verify-opt')
    else:
        form = UserRegisterForm()
        # print("User can not be registered")
    
    context = {
        "form":form
    }

    return render(request,'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request,"Vous etes deja connecté")
        return redirect("core:dashboard")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # print("Email:", email)
        # print("Password:", password)

        if not email or not password:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "auth/login.html")

       
        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Email ou mot de passe incorrect.")
            return render(request, "auth/login.html")
        

        try:
            virtual_account = VirtualAccount.objects.get(owner=user)
        except VirtualAccount.DoesNotExist:
            messages.error(request, "Compte virtuel introuvable.")
            return render(request, "auth/login.html")


        if not virtual_account.is_active:
            messages.warning(
                request,
                "Votre compte n’est pas encore activé."
            )
            return redirect("userauths:verify-otp")
        
        login(request, user)
        messages.success(request, "Connexion réussie.")    

    return render(request, 'auth/login.html')


def verify_otp_view(request):
    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = OTP.objects.get(code=code, is_expire=False)

            if otp.expire_at < timezone.now():
                messages.error(request, "Le code OTP a expiré.")
                otp.is_expire = True
                otp.save()
                return redirect("userauths:verify-otp")

            # Activation du compte virtuel
            virtual_account = VirtualAccount.objects.get(owner=request.user)
            virtual_account.is_active = True
            virtual_account.save()

            # Mise à jour du statut utilisateur
            request.user.status = "ACTIVE"
            request.user.save()

            otp.is_expire = True
            otp.save()

            messages.success(request, "Compte activé avec succès.")
            return redirect("core:dashboard")

        except OTP.DoesNotExist:
            messages.error(request, "Code OTP invalide.")

    return render(request, "auth/verify_otp.html")



def logout_view(request, peanout):
    logout(request)
    messages.success(request, "Vous etes déconnecté")
    return redirect("core:accueil")