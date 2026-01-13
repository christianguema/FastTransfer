from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from userauths.models import User, OTP
from ...decorators import *
from core.forms.retrait_form import widrawForm
from core.forms.deposit_form import DepositForm
from core.forms.transfer_form import TransferForm
from core.models import VirtualAccount, AccountOwner, Transactions, TypeTransaction, TransactionStatus, Platform
from core.utils import create_and_send_otp, verify_otp, invalidate_otp, get_active_otp



def acceuil_view(request):
    return render(request, "accueil/index.html")


@login_required
@allowed_user(allowed_roles=["custumer"])
def user_dashboard_view(request):
    account_owner = AccountOwner.objects.filter(owner=request.user).first()
    va = None
    recent_transactions = None
    if account_owner:
        va = VirtualAccount.objects.filter(owner=account_owner).first()
        if va:

            recent_transactions = Transactions.objects.filter(
                models.Q(sender_account=va) | models.Q(receiver_account=va)
            ).exclude(types=TypeTransaction.FEE).order_by('-created_at')[:5]

    if request.user.status == 'SUSPENDED':
        messages.warning(request,"Votre compte virtuel à été géler par l'administrateur pour des évantuelle raison, veillez attendre la réactivation de votre compte!!")

    return render(request,"user_pages/dashboard.html",  {"virtual_account": va, "recent_transactions": recent_transactions})

@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def deposit_view(request):
    form = DepositForm(request.POST or None)

     # récupérer account_owner et virtual account (pour GET et POST)
    account_owner = AccountOwner.objects.filter(owner=request.user).first()
    va = None
    recent_transactions = []

    if account_owner:
        va = VirtualAccount.objects.filter(owner=account_owner).first()
        if va:
            recent_transactions = Transactions.objects.filter(
                models.Q(sender_account=va) | models.Q(receiver_account=va),
                types=TypeTransaction.DEPOSIT
            ).order_by('-created_at')[:5]


    if request.method == "POST" and form.is_valid():
        amount = form.cleaned_data['amount']

        # Récupérer AccountOwner / VirtualAccount de l'utilisateur connecté
        try:
            account_owner = AccountOwner.objects.get(owner=request.user)
        except AccountOwner.DoesNotExist:
            messages.error(request, "Compte propriétaire introuvable. Contactez le support.")
            return redirect('core:deposit')

        try:
            va = VirtualAccount.objects.get(owner=account_owner)
        except VirtualAccount.DoesNotExist:
            messages.error(request, "Compte virtuel introuvable.")
            return redirect('core:deposit')

        # Créditer le compte
        try:
            # amount fields are integer in your model
            va.balance = (va.balance or 0) + int(amount)
            va.save()
        except Exception as e:
            messages.error(request, "Impossible de créditer le compte.")
            return redirect('core:deposit')

        # Enregistrer la transaction (deposit)
        tx = Transactions.objects.create(
            reference = f"DEP-{request.user.id}-{int(va.balance)}-{Transactions.objects.count()+1}",
            types = TypeTransaction.DEPOSIT,
            amount = str(amount),
            fee = 0,
            net_amount = int(amount),
            status = TransactionStatus.SUCCESS,
            sender_account = va,   # pour dépôt on met sender = va (ou null selon logique)
            receiver_account = va
        )

        #Recupérer les 5 transaction de type deposit recentes de l'utilisateur
        

        messages.success(request, f"Dépôt de {amount}FCFA effectué avec succès. Nouveau solde : {va.balance} FCFA.")
        return redirect('core:user_dash')  # rediriger vers dashboard

    return render(request, "user_pages/deposite_page.html", {"form": form, "recent_transactions": recent_transactions, "virtual_account": va})


@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def withdraw_view(request):
    form = widrawForm(request.POST or None)

    account_owner = AccountOwner.objects.filter(owner=request.user).first()

    va = VirtualAccount.objects.filter(owner=account_owner).first()

    recent_transactions = Transactions.objects.filter(
        models.Q(sender_account=va) | models.Q(receiver_account=va),
        types=TypeTransaction.WITHDRAWAL
    ).order_by('-created_at')[:5]

    if form.is_valid():
        amount = form.cleaned_data['amount']
        
        # Récupérer le compte virtuel de l'utilisateur
        account_owner = AccountOwner.objects.filter(owner=request.user).first()
        if not account_owner:
            messages.error(request, "Compte propriétaire introuvable.")
            return redirect('core:withdraw')
        
        va = VirtualAccount.objects.filter(owner=account_owner).first()
        if not va:
            messages.error(request, "Compte virtuel introuvable.")
            return redirect('core:withdraw')
        
        # Vérifier le solde
        if (va.balance or 0) < int(amount):
            messages.error(request, "Solde insuffisant pour effectuer ce retrait.")
            return redirect('core:withdraw')
        
        # Stocker les informations de retrait en session
        request.session['withdrawal_amount'] = int(amount)
        request.session['withdrawal_user_id'] = request.user.id
        
        # Générer et envoyer l'OTP
        otp_code = create_and_send_otp(request.user)
        messages.success(request, f"Code OTP envoyé à {request.user.email}")
        
        context = {
            "amount": amount,
            "user_email": request.user.email
        }

        return render(request, "user_pages/confirm_widraw_page.html", context)

    context = {
        "form": form,
        "recent_transactions": recent_transactions,
    }
    return render(request, "user_pages/retrait_page.html", context)


@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def confirm_widraw_otp_view(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        # Récupérer le montant de la session
        withdrawal_amount = request.session.get('withdrawal_amount')
        if not withdrawal_amount:
            messages.error(request, "Session expirée. Veuillez recommencer.")
            return redirect('core:withdraw')
        
        # Vérifier l'OTP
        is_valid, message = verify_otp(request.user, otp_code)
        
        if not is_valid:
            return render(request, "user_pages/confirm_widraw_page.html", {
                "error": message,
                "amount": withdrawal_amount,
                "user_email": request.user.email
            })
        
        # L'OTP est valide, procéder au retrait
        try:
            # Récupérer les comptes
            account_owner = AccountOwner.objects.filter(owner=request.user).first()
            va = VirtualAccount.objects.filter(owner=account_owner).first()
            
            # Récupérer le taux de frais de la plateforme
            platform = Platform.objects.first()
            fee_rate = platform.withdrawal_fee_rate if platform else 0
            
            # Calculer les frais (en pourcentage)
            fee = int(withdrawal_amount * fee_rate / 100)
            
            with transaction.atomic():
                # 1. Créer la transaction de retrait (WITHDRAWAL)
                withdrawal_tx = Transactions.objects.create(
                    reference=f"WTH-{request.user.id}-{Transactions.objects.count()+1}",
                    types=TypeTransaction.WITHDRAWAL,
                    amount=str(withdrawal_amount),
                    fee=0,
                    net_amount=withdrawal_amount,
                    status=TransactionStatus.SUCCESS,
                    sender_account=va,
                    receiver_account=va
                )
                
                # 2. Créer la transaction de frais (FEE)
                if fee > 0:
                    fee_tx = Transactions.objects.create(
                        reference=f"FEE-{request.user.id}-{Transactions.objects.count()+1}",
                        types=TypeTransaction.FEE,
                        amount=str(fee),
                        fee=fee,
                        net_amount=0,
                        status=TransactionStatus.SUCCESS,
                        sender_account=va,
                        receiver_account=va
                    )
                
                # 3. Mettre à jour le solde du compte
                total_deducted = withdrawal_amount - fee
                va.balance = (va.balance or 0) - total_deducted
                va.save()
                
                # 4. Invalider l'OTP
                invalidate_otp(request.user)
                
                # 5. Nettoyer la session
                del request.session['withdrawal_amount']
                
                messages.success(request, f"Retrait de {withdrawal_amount} FCFA effectué. Frais: {fee} FCFA. Nouveau solde: {va.balance} FCFA")
                return redirect('core:user_dash')
        
        except Exception as e:
            messages.error(request, f"Erreur lors du retrait: {str(e)}")
            return redirect('core:withdraw')
    
    return redirect("core:withdraw")



@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def transfer_view(request):
    from types import SimpleNamespace
    form = TransferForm(request.POST or None)
    # sender virtual account
    account_owner = AccountOwner.objects.filter(owner=request.user).first()
    va_sender = None
    recent_qs = []
    if account_owner:
        va_sender = VirtualAccount.objects.filter(owner=account_owner).first()
        if va_sender:
            recent_qs = Transactions.objects.filter(
                models.Q(sender_account=va_sender) | models.Q(receiver_account=va_sender),
                types=TypeTransaction.TRANSFER
            ).order_by('-created_at')[:10]

    # build display list with recipient name/contact for template
    recent_display = []
    for tx in recent_qs:
        # determine counterpart virtual account (the other party)
        counterpart_va = None
        direction = 'out'
        try:
            if tx.sender_account and va_sender and tx.sender_account.id == va_sender.id:
                counterpart_va = tx.receiver_account
                direction = 'out'
            else:
                counterpart_va = tx.sender_account
                direction = 'in'
        except Exception:
            counterpart_va = tx.receiver_account or tx.sender_account

        recipient_name = ''
        contact = ''
        try:
            if counterpart_va and getattr(counterpart_va, 'owner', None):
                user_obj = getattr(counterpart_va.owner, 'owner', None)
                if user_obj:
                    recipient_name = ' '.join(filter(None, [getattr(user_obj,'first_name',''), getattr(user_obj,'last_name','')])) or getattr(user_obj,'username', '')
                    contact = getattr(user_obj,'phone','')
        except Exception:
            pass

        recent_display.append(SimpleNamespace(
            reference = getattr(tx,'reference', ''),
            created_at = getattr(tx,'created_at', None),
            amount = getattr(tx,'amount', ''),
            status = getattr(tx,'status', ''),
            recipient_name = recipient_name,
            contact = contact,
            direction = direction
        ))

    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data['phone'].strip()
        amount = int(form.cleaned_data['amount'])

        if not va_sender:
            messages.error(request, "Compte virtuel émetteur introuvable.")
            return redirect('core:transfer')

        if amount <= 0:
            messages.error(request, "Montant invalide.")
            return redirect('core:transfer')

        if (va_sender.balance or 0) < amount:
            messages.error(request, "Solde insuffisant.")
            return redirect('core:transfer')

        # find recipient user by phone
        try:
            recipient = User.objects.get(phone=phone)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur destinataire introuvable.")
            return redirect('core:transfer')

        if recipient == request.user:
            messages.error(request, "Vous ne pouvez pas vous transférer de l'argent.")
            return redirect('core:transfer')

        # find recipient virtual account
        recipient_owner = AccountOwner.objects.filter(owner=recipient).first()
        if not recipient_owner:
            messages.error(request, "Le destinataire n'a pas de compte actif sur la plateforme.")
            return redirect('core:transfer')

        va_recipient = VirtualAccount.objects.filter(owner=recipient_owner).first()
        if not va_recipient:
            messages.error(request, "Compte virtuel du destinataire introuvable.")
            return redirect('core:transfer')

        # perform atomic transfer
        try:
            with transaction.atomic():
                va_sender.balance = (va_sender.balance or 0) - amount
                va_sender.save()

                va_recipient.balance = (va_recipient.balance or 0) + amount
                va_recipient.save()

                tx = Transactions.objects.create(
                    reference = f"TRF-{request.user.id}-{Transactions.objects.count()+1}",
                    types = TypeTransaction.TRANSFER,
                    amount = str(amount),
                    fee = 0,
                    net_amount = int(amount),
                    status = TransactionStatus.SUCCESS,
                    sender_account = va_sender,
                    receiver_account = va_recipient
                )
        except Exception as e:
            messages.error(request, "Erreur lors du transfert. Réessayez plus tard.")
            return redirect('core:transfer')

        messages.success(request, f"Transfert de {amount} FCFA vers {recipient.phone} effectué.")
        return redirect('core:user_dash')

    return render(request, "user_pages/transfer_page.html", {"form": form, "recent_transactions": recent_display, "virtual_account": va_sender})




@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def history_view(request):
    """Afficher l'historique des transactions de l'utilisateur selon les types (sans FEE)"""
    account_owner = AccountOwner.objects.filter(owner=request.user).first()
    
    deposits = []
    transfers = []
    withdrawals = []
    
    if account_owner:
        va = VirtualAccount.objects.filter(owner=account_owner).first()
        if va:
            # Récupérer toutes les transactions (sauf FEE)
            all_txs = Transactions.objects.filter(
                models.Q(sender_account=va) | models.Q(receiver_account=va)
            ).exclude(types=TypeTransaction.FEE).order_by('-created_at')
            
            # Grouper par type
            for tx in all_txs:
                if tx.types == TypeTransaction.DEPOSIT:
                    deposits.append(tx)
                elif tx.types == TypeTransaction.TRANSFER:
                    transfers.append(tx)
                elif tx.types == TypeTransaction.WITHDRAWAL:
                    withdrawals.append(tx)
    
    context = {
        "deposits": deposits,
        "transfers": transfers,
        "withdrawals": withdrawals,
        "virtual_account": account_owner.owner if account_owner else None
    }
    
    return render(request, "user_pages/history_page.html", context)




@login_required
@allowed_user(allowed_roles=["custumer"])
@active_user_only
def resend_otp_view(request):
    """Renvoyer un code OTP à l'utilisateur"""
    if request.method == 'POST':
        try:
            # Vérifier qu'il y a un OTP actif de l'utilisateur
            old_otp = get_active_otp(request.user)
            
            # Générer et envoyer un nouveau code
            otp_code = create_and_send_otp(request.user)
            
            # Invalider l'ancien OTP
            if old_otp:
                old_otp.is_expire = True
                old_otp.save()
            
            return render(request, "user_pages/confirm_widraw_page.html", {
                "amount": request.session.get('withdrawal_amount'),
                "user_email": request.user.email,
                "resent": True
            })
        except Exception as e:
            messages.error(request, f"Erreur lors du renvoi du code: {str(e)}")
            return redirect('core:withdraw')
    
    return redirect('core:withdraw')

