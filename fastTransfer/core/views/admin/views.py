from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from rest_framework import renderers
from userauths.models import User, UserSatus
from ...decorators import *
from core.forms.platform_form import PlatformForm
from core.models import VirtualAccount, AccountOwner, Transactions, TypeTransaction, TransactionStatus, Platform



@login_required 
@admin_only
def admin_dashbord_view(request):
    return render(request, "admin_pages/dashboard.html")


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
            try:
                va = VirtualAccount.objects.get(owner__owner=target)
                va.is_active = False
                va.save()
            except VirtualAccount.DoesNotExist:
                pass
            messages.success(request, f"Utilisateur {target} suspendu.")
        elif action == 'reactivate':
            target.status = UserSatus.ACTIVE
            target.save()
            try:
                va = VirtualAccount.objects.get(owner__owner=target)
                va.is_active = True
                va.save()
            except VirtualAccount.DoesNotExist:
                pass
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
    ).order_by('-created_at')[:20]

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
