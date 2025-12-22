from django.urls import path
from userauths import views

app_name = 'userauths'

urlpatterns = [
    path('register/', views.register_views, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("verify-otp/", views.verify_otp_view, name="verify-otp"),
]

