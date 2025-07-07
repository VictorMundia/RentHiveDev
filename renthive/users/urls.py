from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    path('owner/bank-details/', views.owner_bank_details, name='owner_bank_details'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
