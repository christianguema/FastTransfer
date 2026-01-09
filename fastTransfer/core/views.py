from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from userauths.models import User
from .decorators import *
from core.forms.deposit_form import DepositForm
from core.forms.transfer_form import TransferForm
from core.models import VirtualAccount, AccountOwner, Transactions, TypeTransaction, TransactionStatus


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
            ).order_by('-created_at')[:10]

    return render(request,"user_pages/dashboard.html",  {"virtual_account": va, "recent_transactions": recent_transactions})

@login_required
@allowed_user(allowed_roles=["custumer"])
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
#@allowed_user(allowed_roles=["custumer"])
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
@admin_only
def admin_dashbord_view(request):
    return render(request, "admin_pages/dashboard.html")