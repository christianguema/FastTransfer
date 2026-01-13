from django.urls import path
from core.views.users import views as user_view
from core.views.admin import views as admin_view

app_name = 'core'

urlpatterns = [
    #Route pour les pages des utlisateurs
    path('', user_view.acceuil_view, name='accueil'),
    path('dashboard/', user_view.user_dashboard_view,name ="user_dash"),  
    path('deposit/', user_view.deposit_view, name="deposite"),
    path('transfer/', user_view.transfer_view, name="transfer"),
    path('withdraw/', user_view.withdraw_view, name="withdraw"),
    path('confirm_withdraw/', user_view.confirm_widraw_otp_view, name="confirm_withdraw_otp"),
    path('resend_otp/', user_view.resend_otp_view, name="resend_otp"),
    path('history/', user_view.history_view, name="history"),


    #Route pour les pages des administrateur
    path('admin_dash/', admin_view.admin_dashbord_view, name="admin_dash"),
    path('user_control/', admin_view.user_view, name="user_page"),
    path('user_control/<int:user_id>/', admin_view.user_detail_view, name="user_detail"),
    path('parameter/', admin_view.parameter_view, name="parameter")
]