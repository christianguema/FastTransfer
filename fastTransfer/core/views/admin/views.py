from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import timedelta
from django.db import models, transaction
from rest_framework import renderers
from userauths.models import User, UserSatus
from ...decorators import *
from core.forms.platform_form import PlatformForm
from core.models import VirtualAccount, AccountOwner, Transactions, TypeTransaction, TransactionStatus, Platform


@login_required 
@admin_only
def admin_dashbord_view(request):
    # 1. Nombre total d'utilisateurs (clients)
    total_users = User.objects.filter(groups__name="custumer").count()
    
    # 2. Nombre de comptes actifs
    active_accounts = User.objects.filter(
        groups__name="custumer",
        status=UserSatus.ACTIVE
    ).count()

    #Compte utilisateur recents inscritts et le sorld de leur compte
    recent_users = User.objects.filter(
        groups__name="custumer"
    ).annotate(
        account_balance=Sum('accountowner__virtualaccount__balance')
    ).order_by('-date_joined')[:5]
    # 3. Nombre de comptes suspendus (utilisateurs suspendus)
    suspended_accounts = User.objects.filter(
        groups__name="custumer",
        status=UserSatus.SUSPENDED
    ).count()

    #frais de commission de la plateforme
    platform = Platform.objects.first()
    commission_rate = platform.withdrawal_fee_rate
    
    # 4. Montant total des commissions (somme des fees des transactions réussies)
    total_commissions = Transactions.objects.filter(
        status=TransactionStatus.SUCCESS
    ).aggregate(Sum('fee'))['fee__sum'] or 0
    
    # 5. Transactions récentes pour le graphique et la table
    recent_transactions = Transactions.objects.filter(
        status=TransactionStatus.SUCCESS
    ).select_related(
        'sender_account__owner__owner',
        'receiver_account__owner__owner'
    ).order_by('-created_at')[:10]
    
    # 6. Total des transactions du mois
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    month_transactions = Transactions.objects.filter(
        status=TransactionStatus.SUCCESS,
        created_at__gte=first_day_of_month,
        created_at__lte=today
    ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    
    # 7. Total des transactions du jour
    today_transactions = Transactions.objects.filter(
        status=TransactionStatus.SUCCESS,
        created_at=today
    ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    
    # 8. Total des transactions (tous les temps)
    total_transaction_volume = Transactions.objects.filter(
        status=TransactionStatus.SUCCESS
    ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    
    context = {
        'recent_user' : recent_users,
        'commission_rate': commission_rate,
        'total_users': total_users,
        'active_accounts': active_accounts,
        'suspended_accounts': suspended_accounts,
        'total_commissions': total_commissions,
        'recent_transactions': recent_transactions,
        'month_revenue': month_transactions,
        'today_revenue': today_transactions,
        'total_volume': total_transaction_volume,
    }
    
    return render(request, "admin_pages/dashboard.html", context)

@login_required
@admin_only
def user_view(request):
    #Selectionner que les utlisateurs avec le groupe customer
    users = User.objects.filter(groups__name="custumer").order_by('-date_joined')

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect(request.path)

        if action == 'suspend':
            target.status = UserSatus.SUSPENDED
            target.save()
            # try:
            #     va = VirtualAccount.objects.get(owner__owner=target)
            #     va.is_active = False
            #     va.save()
            # except VirtualAccount.DoesNotExist:
            #     pass
            messages.success(request, f"Utilisateur {target} suspendu.")
        elif action == 'reactivate':
            target.status = UserSatus.ACTIVE
            target.save()
            # try:
            #     va = VirtualAccount.objects.get(owner__owner=target)
            #     va.is_active = True
            #     va.save()
            # except VirtualAccount.DoesNotExist:
            #     pass
            messages.success(request, f"Utilisateur {target} réactivé.")
        else:
            messages.error(request, "Action non reconnue.")
        return redirect(request.path)


    context = {'users': users}
    return render(request, "admin_pages/users_page.html", context)


@login_required
@admin_only
def user_detail_view(request, user_id):
    target = get_object_or_404(User, id=user_id)

    # virtual account (may not exist)
    try:
        va = VirtualAccount.objects.get(owner__owner=target)
    except VirtualAccount.DoesNotExist:
        va = None

    # recent transactions where user is sender or receiver
    txs = Transactions.objects.filter(
        models.Q(sender_account__owner__owner=target) | models.Q(receiver_account__owner__owner=target)
    ).order_by('-created_at')[:10]

    last_login = target.last_login

    context = {
        'target_user': target,
        'virtual_account': va,
        'transactions': txs,
        'last_login': last_login,
    }
    return render(request, "admin_pages/user_detail.html", context)


@login_required
@admin_only
def parameter_view(request):
    form = PlatformForm()
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            if Platform.objects.exists():
                platform = Platform.objects.first()
                platform.name = form.cleaned_data['name']
                platform.withdrawal_fee_rate = form.cleaned_data['withdrawal_fee_rate']
                platform.save()
                messages.success(request, "Paramètres de la plateforme mis à jour avec succès.")
            else:
                form.save() 
                messages.success(request, "Paramètres de la plateforme créés avec succès.")
        else:
            messages.error(request, "Erreur lors de la mise à jour des paramètres de la plateforme.")
    context = {'form': form}
    return render(request, "admin_pages/paramater_page.html", context)
