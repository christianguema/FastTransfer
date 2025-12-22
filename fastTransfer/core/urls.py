from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.acceuil_view, name='accueil'),
    path('dashboard/', views.dashborad_view,name ="dashboard")
    
]