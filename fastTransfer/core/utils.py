import random
import string
from django.core.mail import send_mail
from django.conf import settings
from userauths.models import OTP
from django.utils import timezone
from datetime import timedelta


def generate_otp(length=6):
    """Générer un code OTP de 6 chiffres"""
    return ''.join(random.choices(string.digits, k=length))


def create_and_send_otp(user, subject="Code OTP FastTransfert"):
    """
    Créer un OTP, l'envoyer par email et retourner le code
    """
    # Supprimer les OTP expirés de cet utilisateur
    OTP.objects.filter(user_otp=user, is_expire=True).delete()
    
    # Générer le code OTP
    otp_code = generate_otp()
    
    # Définir l'expiration à 3 minutes
    expire_at = timezone.now() + timedelta(minutes=3)
    
    # Créer l'OTP en base de données
    otp_obj = OTP.objects.create(
        user_otp=user,
        code=otp_code,
        is_expire=False,
        expire_at=expire_at
    )
    
    # Envoyer par email
    message = f"""
    Bonjour {user.first_name},
    
    Votre code OTP pour confirmer votre retrait est : {otp_code}
    
    Ce code expirera dans 3 minutes.
    
    Si vous n'avez pas demandé ce retrait, ignorez ce message.
    
    Cordialement,
    L'équipe FastTransfert
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
    
    return otp_code


def verify_otp(user, otp_code):
    """
    Vérifier le code OTP de l'utilisateur
    Retourne (is_valid, message)
    """
    try:
        otp_obj = OTP.objects.get(user_otp=user, code=otp_code)
        
        # Vérifier si expiré
        if otp_obj.is_expired():
            otp_obj.is_expire = True
            otp_obj.save()
            return False, "Code OTP expiré"
        
        # Vérifier si déjà marqué comme expiré
        if otp_obj.is_expire:
            return False, "Code OTP déjà utilisé ou expiré"
        
        return True, "Code OTP valide"
    
    except OTP.DoesNotExist:
        return False, "Code OTP invalide"
    except Exception as e:
        return False, f"Erreur: {str(e)}"


def invalidate_otp(user):
    """Invalider tous les OTP actifs de l'utilisateur"""
    OTP.objects.filter(user_otp=user, is_expire=False).update(is_expire=True)


def get_active_otp(user):
    """Récupérer l'OTP actif de l'utilisateur"""
    try:
        return OTP.objects.get(user_otp=user, is_expire=False)
    except OTP.DoesNotExist:
        return None
