import smtplib
import socket
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from userauths.forms import UserRegisterForm
from userauths.models import User, OTP
from userauths.utils import generate_otp, otp_login_expiration
from core.models import VirtualAccount, AccountOwner
from django.contrib.auth.models import Group


def send_otp_email(request, user, otp_code):
    try :
        send_mail(
            subject="Activation de votre compte FastTransfer",
            message=f"""
                Bonjour {user.first_name} {user.last_name},

                Voici votre code d’activation de compte: {otp_code}

                Ce code expire dans 2 minutes.
                """,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )
        return True
    except (smtplib.SMTPException, socket.gaierror, ConnectionError, TimeoutError):
        return False
    

def register_views(request):
    if(request.method == "POST"):
        form = UserRegisterForm(request.POST or None)
        if(form.is_valid()):
            try:
                new_user = form.save(commit=False)
                new_user.status = "PENDING"
                new_user.save()
                # print(f" User created: {new_user.id}")
                
                # Créer ou obtenir le groupe avec correction typo
                group, created = Group.objects.get_or_create(name="custumer")
                new_user.groups.add(group)
                # print(f" Group assigned: {group.name}")
                
                account_owner = AccountOwner.objects.create(owner=new_user)
                # print(f" AccountOwner created: {account_owner.id}")

                virtual_account = VirtualAccount.objects.create(
                    owner=account_owner,
                    balance=0,
                    is_active=False
                )
                # print(f" VirtualAccount created: {virtual_account.id}")
                
                # Code d'activation
                otp_code = generate_otp()
                expire_at = otp_login_expiration()
                # print(f" OTP code generated: {otp_code}")

                otp = OTP.objects.update_or_create(
                    user_otp=new_user,
                    defaults={
                        "code":otp_code,
                        "is_expire":False,
                        "expire_at": expire_at
                    }
                )
                # print(f" OTP created/updated")

                # Stocker l'utilisateur en session
                request.session['user_otp_id'] = new_user.id
                # print(f" Session stored: user_otp_id = {new_user.id}")

                success = send_otp_email(request, new_user, otp_code)
                # print(f" Email sent: {success}")

                if not success:
                    messages.error(
                        request,
                        "Impossible d'envoyer l'email. Vérifiez votre connexion internet et réessayez"
                    )
                    # print(" Email send failed, returning form")
                    return render(request, "auth/register.html", {"form": form})

                messages.success(request,"Compte créé. Veuillez vérifier votre email pour l'activation.")
                # print(f" Redirecting to verify-otp")
                return redirect('userauths:verify-otp')
                
            except Exception as e:
                # print(f"✗ Exception occurred: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
                return render(request, "auth/register.html", {"form": form})
    else:
        form = UserRegisterForm()
    
    context = {"form": form}
    return render(request,'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:  
        if request.user.role == "ADMIN":
            return redirect("core:admin_dash")
        else:
            return redirect("core:user_dash")

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
        
        if user.role == "ADMIN":
            login(request, user)
            return redirect("core:admin_dash")
        else:
            try:
                account_owner = AccountOwner.objects.get(owner=user)
            except AccountOwner.DoesNotExist:
                messages.error(request, "Compte utilisateur incomplet ou innexistant.")
                return render(request, "auth/login.html")

            try:
                virtual_account = VirtualAccount.objects.get(owner=account_owner)
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

            return redirect("core:user_dash")  
        
    return render(request, 'auth/login.html')


def verify_otp_view(request):
    otp = None
    user = None
    account_owner = None

    # 1) récupérer l'utilisateur ciblé pour l'activation
    user_id = request.session.get('user_otp_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None

    # si l'utilisateur est connecté et qu'on n'a pas d'id en session, on peut utiliser request.user
    if not user and request.user.is_authenticated:
        user = request.user

    # si on a un user, essayer d'obtenir son AccountOwner (peut être absent)
    if user:
        try:
            account_owner = AccountOwner.objects.get(owner=user)
        except AccountOwner.DoesNotExist:
            account_owner = None

    if request.method == "POST":
        # --- RENVOI DU CODE ---
        if 'resend' in request.POST:
            if not user:
                messages.error(request, "Impossible de renvoyer le code (utilisateur introuvable).")
                return redirect('userauths:verify-otp')

            new_code = generate_otp()
            expire_at = otp_login_expiration()

            # update_or_create sur le champ user_otp
            otp_obj, created = OTP.objects.update_or_create(
                user_otp=user,
                defaults={
                    "code": new_code,
                    "is_expire": False,
                    "expire_at": expire_at
                }
            )

            success = send_otp_email(request, user, new_code)
            if not success:
                messages.error(request, "Impossible d'envoyer l'email. Vérifiez la connexion.")
                return redirect('userauths:verify-otp')

            # conserver user_id en session (déjà fait à l'inscription)
            request.session['user_otp_id'] = user.id

            messages.success(request, "Un nouveau code a été envoyé à votre email.")
            return redirect('userauths:verify-otp')

        # --- VERIFICATION DU CODE ---
        if 'verify' in request.POST:
            code = request.POST.get("otp", "").strip()
            if not code:
                messages.error(request, "Veuillez entrer le code OTP.")
                return redirect('userauths:verify-otp')

            # Chercher l'OTP pour cet utilisateur et code (sécurité contre collision)
            try:
                otp = OTP.objects.get(code=code, is_expire=False, user_otp=user)
            except OTP.DoesNotExist:
                messages.error(request, "Code OTP invalide.")
                return redirect('userauths:verify-otp')

            # Vérifier expiration
            if otp.expire_at < timezone.now():
                otp.is_expire = True
                otp.save()
                messages.error(request, "Le code OTP a expiré. Vous pouvez demander un nouveau code.")
                return redirect('userauths:verify-otp')

            # Activer le compte virtuel via AccountOwner -> VirtualAccount
            try:
                account_owner = AccountOwner.objects.get(owner=user)
            except AccountOwner.DoesNotExist:
                messages.error(request, "Compte utilisateur incomplet (AccountOwner manquant).")
                return redirect('userauths:verify-otp')

            try:
                virtual_account = VirtualAccount.objects.get(owner=account_owner)
                virtual_account.is_active = True
                virtual_account.save()
            except VirtualAccount.DoesNotExist:
                messages.error(request, "Compte virtuel introuvable (activation impossible).")
                return redirect('userauths:verify-otp')

            # Mettre à jour le statut utilisateur
            user.status = "ACTIVE"
            user.save()

            # Marquer OTP comme utilisé
            otp.is_expire = True
            otp.save()

            # Nettoyer la session (optionnel)
            request.session.pop('user_otp_id', None)

            # Connexion automatique et redirection
            login(request, user)
            messages.success(request, "Compte activé avec succès.")
            return redirect('core:user_dash')

    # Préparer le contexte : OTP courant (non expiré) pour affichage
    if user:
        otp = OTP.objects.filter(user_otp=user, is_expire=False).order_by('-expire_at').first()

    context = {"otp_code": otp}
    return render(request, "auth/verify-otp.html", context)

def logout_view(request):
    logout(request)
    return redirect("core:accueil")