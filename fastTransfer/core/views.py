from django.shortcuts import render

# Create your views here.

def acceuil_view(request):
    return render(request, "accueil/index.html")


def dashborad_view(request):
    return render(request,"partials/base.html")