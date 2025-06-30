from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('tenant/profile/', views.tenant_profile, name='tenant_profile'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('lipa-na-mpesa/', views.lipa_na_mpesa, name='lipa_na_mpesa'),
    path('card-payment/', views.card_payment, name='card_payment'),
    path('bank-transfer/', views.bank_transfer, name='bank_transfer'),
]
