from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .decorators import *
from core.forms.deposit_form import DepositForm
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
@allowed_user(allowed_roles=["custumer"])
def transfer_view(request):
    return render(request, "user_pages/transfer_page.html")




@login_required 
def admin_dashbord_view(request):
    return render(request, "admin_pages/dashboard.html")