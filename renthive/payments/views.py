from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Payment
from properties.models import Lease
from django.conf import settings

# Create your views here.
def make_payment(request):
    return render(request, 'payments/make_payment.html')

@login_required
def confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, lease__unit__property__owner=request.user)
    if request.method == 'POST':
        payment.is_confirmed = True
        payment.save()
        messages.success(request, f"Payment of ${payment.amount} confirmed.")
        # Send confirmation email to tenant
        tenant_email = payment.lease.tenant.email
        send_mail(
            subject="Rent Payment Confirmed",
            message=f"Your rent payment of ${payment.amount} for unit {payment.lease.unit.unit_number} has been confirmed.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[tenant_email],
            fail_silently=True,
        )
        return redirect('payments:owner_payments')
    return render(request, 'payments/confirm_payment.html', {'payment': payment})

@login_required
def owner_payments(request):
    leases = Lease.objects.filter(unit__property__owner=request.user)
    payments = Payment.objects.filter(lease__in=leases).order_by('-payment_date')
    return render(request, 'payments/owner_payments.html', {'payments': payments})
