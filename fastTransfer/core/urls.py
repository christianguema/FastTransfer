from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.acceuil_view, name='accueil'),
    path('dashboard/', views.user_dashboard_view,name ="user_dash"),
    path('admin_dash/', views.admin_dashbord_view, name="admin_dash"),
    path('deposit/', views.deposit_view, name="deposite"),
    path('transfer/', views.transfer_view, name="transfer"),
]