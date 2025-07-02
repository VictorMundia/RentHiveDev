from django.contrib.auth.decorators import login_required  # Import decorator to require user login for views
from django.contrib import messages  # Import messages framework for user notifications
from django.core.mail import send_mail  # Import function to send emails
from django.shortcuts import render, get_object_or_404, redirect  # Import shortcuts for rendering templates, fetching objects, and redirects
from django.utils import timezone  # Import timezone utilities (not used in this code)
from .models import Payment  # Import Payment model from current app
from properties.models import Lease  # Import Lease model from properties app
from django.conf import settings  # Import settings to access project configuration

# Create your views here.
def make_payment(request):  # Define view for making a payment
    return render(request, 'payments/make_payment.html')  # Render the make_payment template

@login_required  # Require user to be logged in to access this view
def confirm_payment(request, payment_id):  # Define view to confirm a payment
    payment = get_object_or_404(Payment, pk=payment_id, lease__unit__property__owner=request.user)  # Fetch payment object or return 404 if not found or not owned by user
    if request.method == 'POST':  # Check if the request is a POST (form submission)
        payment.is_confirmed = True  # Mark payment as confirmed
        payment.save()  # Save changes to the database
        messages.success(request, f"Payment of ${payment.amount} confirmed.")  # Add a success message for the user
        # Send confirmation email to tenant
        tenant_email = payment.lease.tenant.email  # Get tenant's email address
        send_mail(
            subject="Rent Payment Confirmed",  # Email subject
            message=f"Your rent payment of ${payment.amount} for unit {payment.lease.unit.unit_number} has been confirmed.",  # Email body
            from_email=settings.DEFAULT_FROM_EMAIL,  # Sender's email address from settings
            recipient_list=[tenant_email],  # List of recipients (tenant)
            fail_silently=True,  # Do not raise errors if email fails
        )
        return redirect('payments:owner_payments')  # Redirect to the owner's payments page
    return render(request, 'payments/confirm_payment.html', {'payment': payment})  # Render confirmation template with payment context

@login_required  # Require user to be logged in to access this view
def owner_payments(request):  # Define view to show all payments for properties owned by the user
    leases = Lease.objects.filter(unit__property__owner=request.user)  # Get all leases for properties owned by the user
    payments = Payment.objects.filter(lease__in=leases).order_by('-payment_date')  # Get all payments for those leases, ordered by date descending
    return render(request, 'payments/owner_payments.html', {'payments': payments})  # Render payments list template with payments context
