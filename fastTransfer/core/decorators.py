from django.http import  HttpResponse
from django.shortcuts import redirect


def allowed_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("Vous n'etes pas autoriser à accéder a cette page!!")
        return wrapper_func
    return decorator


#Décorateur pour autorisé seulement les utilisateur actives a éffectuer les opérations (retrait, depot et transfert)
def active_user_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.status == 'ACTIVE':
            return view_func(request, *args, **kwargs)
        elif request.user.status == "SUSPENDED":
            return HttpResponse("Votre compte est suspendu. Veuillez contacter l'administrateur."
                                " Vous ne pouvez pas effectuer cette opération.")
        else:
            return HttpResponse("Accès non autorisé!!")
    return wrapper_func


def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        
        if group == "customer":
            return redirect()
        if group == "admins":
            return view_func(request, *args, **kwargs)
        
    return wrapper_func