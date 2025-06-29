from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('make/', views.make_payment, name='make_payment'),
    path('owner/', views.owner_payments, name='owner_payments'),
    path('confirm/<int:payment_id>/', views.confirm_payment, name='confirm_payment'),
]
