from django.contrib.auth import authenticate

def custom_login(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_type = request.POST.get('user_type')  # 'tenant' or 'owner'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.user_type == selected_type:
                login(request, user)
                if user.user_type == 'owner':
                    return redirect('users:profile')
                elif user.user_type == 'tenant':
                    return redirect('users:tenant_profile')
            else:
                error_message = 'User type does not match your profile. Please select the correct type.'
        else:
            error_message = 'Invalid username or password.'
    return render(request, 'users/login.html', {'error_message': error_message})

from django.contrib.auth import logout, login  # Import logout and login functions for authentication
from django.contrib import messages  # Import messages framework for user notifications
from django.shortcuts import redirect, render, get_object_or_404  # Import shortcuts for common view operations
from django.contrib.auth.decorators import login_required  # Import decorator to require login for views
from django.urls import reverse  # Import reverse for URL resolution
from django.http import HttpResponseRedirect, JsonResponse  # Import HTTP response classes
from properties.models import Lease, Unit, Property  # Import models from properties app
from payments.models import Payment  # Import Payment model
from maintenance.models import MaintenanceRequest  # Import MaintenanceRequest model
from .forms import RegisterForm  # Import registration form
from .forms_message import MessageForm  # Import message form for chat
from .models_message import Message  # Import Message model for chat
from .models import User  # Import custom User model
from users.forms import OwnerBankAccountForm  # Import owner bank account form
from users.models_bank import OwnerBankAccount  # Import OwnerBankAccount model
from django.utils import timezone  # Import timezone utilities
from django.db import models  # Import Django models module
from django.core.mail import send_mail  # Import send_mail for email notifications
from django.conf import settings  # Import settings for configuration
from django.views.decorators.csrf import csrf_exempt  # Import CSRF exemption decorator
import json  # Import json for parsing JSON data
from payments.mpesa import stk_push  # Import stk_push for Mpesa payments

@login_required
def inbox(request):
    # Only tenants can access their inbox
    if not request.user.user_type == 'tenant':
        return redirect('users:dashboard')
    from properties.models import Lease
    from .forms_message import MessageForm
    # Find the most recent lease for this tenant
    lease = Lease.objects.filter(tenant=request.user).order_by('-start_date').first()
    owner = lease.unit.property.owner if lease else None
    send_form = MessageForm()
    sent_success = False

    # Show all messages between tenant and owner (both directions)
    if owner:
        messages_list = Message.objects.filter(
            (models.Q(sender=request.user) & models.Q(recipient=owner)) |
            (models.Q(sender=owner) & models.Q(recipient=request.user))
        ).order_by('sent_at')
    else:
        messages_list = Message.objects.filter(recipient=request.user).order_by('sent_at')

    if owner and request.method == 'POST' and 'send_message' in request.POST:
        # Only body is required for chat
        send_form = MessageForm(request.POST)
        send_form.fields.pop('subject', None)
        if send_form.is_valid():
            msg = send_form.save(commit=False)
            msg.sender = request.user
            msg.recipient = owner
            msg.subject = ''
            msg.save()
            sent_success = True
            send_form = MessageForm()
            send_form.fields.pop('subject', None)

    # Remove subject field for chat UI
    send_form.fields.pop('subject', None)

    return render(request, 'users/inbox.html', {
        'messages_list': messages_list,
        'send_form': send_form,
        'sent_success': sent_success,
        'owner': owner
    })

@login_required
def send_message(request, tenant_id):
    tenant = get_object_or_404(User, pk=tenant_id, user_type='tenant')
    # Show all messages between owner and tenant (both directions)
    messages_list = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(recipient=tenant)) |
        (models.Q(sender=tenant) & models.Q(recipient=request.user))
    ).order_by('sent_at')
    sent_success = False
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                sender=request.user,
                recipient=tenant,
                subject='',
                body=body
            )
            sent_success = True
    return render(request, 'users/send_message.html', {
        'tenant': tenant,
        'messages_list': messages_list,
        'sent_success': sent_success,
        'form': MessageForm()
    })
@login_required
def owner_bank_details(request):
    if not request.user.user_type == 'owner':  # Check if user is an owner
        return redirect('users:dashboard')  # Redirect non-owners to dashboard
    try:
        bank_account = request.user.bank_account  # Try to get user's bank account
        form = OwnerBankAccountForm(instance=bank_account)  # Pre-fill form with existing data
    except OwnerBankAccount.DoesNotExist:  # If no bank account exists
        form = OwnerBankAccountForm()  # Create empty form
    if request.method == 'POST':  # If form is submitted
        form = OwnerBankAccountForm(request.POST, instance=getattr(request.user, 'bank_account', None))  # Bind form to POST data
        if form.is_valid():  # Validate form
            bank = form.save(commit=False)  # Create bank object but don't save yet
            bank.owner = request.user  # Set owner to current user
            bank.save()  # Save bank account
            messages.success(request, "Bank details saved successfully.")  # Show success message
            return redirect('users:profile')  # Redirect to profile
    return render(request, 'users/owner_bank_details.html', {'form': form})  # Render form template


@login_required
def dashboard(request):
    context = {}
    if request.user.user_type == 'tenant':
        lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
        payments = Payment.objects.filter(lease=lease).order_by('-payment_date')[:5] if lease else []
        maintenance_requests = MaintenanceRequest.objects.filter(requested_by=request.user).order_by('-created_at')[:5]
        context.update({
            'lease': lease,
            'payments': payments,
            'maintenance_requests': maintenance_requests,
        })
    elif request.user.user_type == 'owner':
        properties = request.user.properties.all()
        units = Unit.objects.filter(property__in=properties)
        leases = Lease.objects.filter(unit__in=units, is_active=True)
        pending_payments = Payment.objects.filter(
            lease__in=leases,
            is_confirmed=False
        ).order_by('-payment_date')[:5]
        pending_requests = MaintenanceRequest.objects.filter(
            unit__in=units,
            status='pending'
        ).order_by('-created_at')[:5]
        from users.models import Notification
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        context.update({
            'properties': properties,
            'pending_payments': pending_payments,
            'pending_requests': pending_requests,
            'notifications': notifications,
        })
    return render(request, 'users/dashboard.html', context)

@login_required  # Require user to be logged in
def profile(request):
    user = request.user  # Get current user
    properties = Property.objects.filter(owner=user)  # Get properties owned by user
    total_properties = properties.count()  # Count total properties
    selected_property = None  # Initialize selected property
    vacant_units = occupied_units = paid_units = unpaid_units = maintenance_requests = None  # Initialize stats
    property_id = request.GET.get('property')  # Get property ID from query params
    if property_id:
        try:
            selected_property = properties.get(pk=property_id)  # Get selected property
            units = selected_property.units.all()  # Get all units in property
            vacant_units = units.filter(status='vacant').count()  # Count vacant units
            occupied_units = units.filter(status='occupied').count()  # Count occupied units
            paid_units = unpaid_units = 0  # Initialize paid/unpaid counters
            for unit in units:  # For each unit
                lease = unit.leases.order_by('-start_date').first()  # Get most recent lease
                if lease:
                    payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()  # Get latest confirmed payment
                    if payment:
                        paid_units += 1  # Increment paid units
                    else:
                        unpaid_units += 1  # Increment unpaid units
            maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()  # Count maintenance requests
        except Property.DoesNotExist:
            selected_property = None  # If property doesn't exist, set to None
    return render(request, 'users/profile.html', {
        'user': user,  # Pass user to template
        'properties': properties,  # Pass properties to template
        'total_properties': total_properties,  # Pass total properties
        'selected_property': selected_property,  # Pass selected property
        'vacant_units': vacant_units,  # Pass vacant units
        'occupied_units': occupied_units,  # Pass occupied units
        'paid_units': paid_units,  # Pass paid units
        'unpaid_units': unpaid_units,  # Pass unpaid units
        'maintenance_requests': maintenance_requests,  # Pass maintenance requests
    })

def register(request):
    from properties.models import Unit  # Import Unit model locally to avoid circular import
    unit_id = request.GET.get('unit')  # Get unit ID from query params
    invited_unit = None  # Initialize invited unit
    if unit_id:
        try:
            invited_unit = Unit.objects.get(pk=unit_id)  # Get invited unit
        except Unit.DoesNotExist:
            invited_unit = None  # If not found, set to None
    if request.method == 'POST':  # If form is submitted
        form = RegisterForm(request.POST)  # Bind form to POST data
        if form.is_valid():  # Validate form
            user = form.save(commit=False)  # Create user object but don't save yet
            user.first_name = form.cleaned_data['first_name']  # Set first name
            user.last_name = form.cleaned_data['last_name']  # Set last name
            user.save()  # Save user
            # If tenant registering via invite, assign to unit and create lease
            if invited_unit and form.cleaned_data.get('user_type') == 'tenant':
                invited_unit.status = 'occupied'  # Mark unit as occupied
                invited_unit.save()  # Save unit
                from properties.models import Lease
                from django.utils import timezone
                Lease.objects.create(
                    unit=invited_unit,
                    tenant=user,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date().replace(year=timezone.now().year + 1),
                    rent_amount=invited_unit.rent_amount,
                    is_active=True  # Ensure lease is active
                )
                request.session['welcome_property'] = invited_unit.property.name  # Store property name in session
            login(request, user)  # Log in user
            if user.user_type == 'owner':  # If owner, redirect to bank details
                return redirect('users:owner_bank_details')
            if user.user_type == 'tenant':
                return redirect('users:dashboard')  # Redirect tenant to dashboard
            return redirect('users:profile')  # Redirect to profile (fallback)
    else:
        form = RegisterForm()  # Create empty registration form
    show_errors = request.method == 'POST'  # Show errors only if form was submitted
    return render(request, 'users/register.html', {'form': form, 'show_errors': show_errors, 'invited_unit': invited_unit})  # Render registration template

@login_required  # Require user to be logged in
def tenant_profile(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user).order_by('-start_date').first()  # Get most recent lease
    unit = lease.unit if lease else None  # Get unit from lease
    payments = Payment.objects.filter(lease=lease).order_by('-payment_date') if lease else []  # Get payments for lease
    maintenance_requests = MaintenanceRequest.objects.filter(requested_by=user).order_by('-created_at')  # Get user's maintenance requests
    rent_balance = 0  # Initialize rent balance
    if lease:
        total_paid = payments.filter(is_confirmed=True).aggregate(total=models.Sum('amount'))['total'] or 0  # Calculate total paid
        rent_balance = lease.rent_amount - total_paid  # Calculate rent balance
    payment_success = False  # Initialize payment success flag
    if request.method == 'POST' and 'pay_rent' in request.POST:  # If rent payment form submitted
        amount = request.POST.get('amount')  # Get amount
        payment_method = request.POST.get('payment_method')  # Get payment method
        transaction_code = request.POST.get('transaction_code')  # Get transaction code
        try:
            amount = float(amount)  # Convert amount to float
            if amount > 0 and lease:
                if payment_method == 'mpesa':  # If Mpesa payment
                    callback_url = request.build_absolute_uri('/users/mpesa/callback/')  # Build callback URL
                    phone_number = user.phone_number  # Get user's phone number
                    account_reference = f"Unit{unit.unit_number}"  # Set account reference
                    transaction_desc = f"Rent payment for {unit.property.name}"  # Set transaction description
                    mpesa_response = stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)  # Initiate Mpesa STK push
                    transaction_code = mpesa_response.get('CheckoutRequestID', '')  # Get transaction code
                payment = Payment.objects.create(
                    lease=lease,  # Assign lease
                    amount=amount,  # Set amount
                    payment_date=timezone.now(),  # Set payment date
                    payment_method=payment_method,  # Set payment method
                    transaction_code=transaction_code,  # Set transaction code
                    is_confirmed=False  # Mark as unconfirmed
                )
                send_mail(
                    subject="Rent Payment Receipt",  # Email subject
                    message=f"Thank you for your payment of ${amount} for unit {unit.unit_number} at {unit.property.name}.",  # Email message
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Sender email
                    recipient_list=[user.email],  # Recipient email
                    fail_silently=True,  # Fail silently
                )
                payment_success = True  # Set payment success flag
        except Exception:
            pass  # Ignore errors
    return render(request, 'users/tenant_profile.html', {
        'lease': lease,  # Pass lease to template
        'unit': unit,  # Pass unit to template
        'payments': payments,  # Pass payments to template
        'maintenance_requests': maintenance_requests,  # Pass maintenance requests
        'rent_balance': rent_balance,  # Pass rent balance
        'payment_success': payment_success,  # Pass payment success flag
    })

def lipa_na_mpesa(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()  # Get active lease
    unit = lease.unit if lease else None  # Get unit from lease
    amount = request.POST.get('amount') or request.GET.get('amount')  # Get amount from POST or GET
    if request.method == 'POST' and 'pay_rent' in request.POST:  # If rent payment form submitted
        phone_number = request.POST.get('mpesa_phone')  # Get Mpesa phone number
        if lease and amount and phone_number:
            try:
                amount = float(amount)  # Convert amount to float
                callback_url = request.build_absolute_uri('/users/mpesa/callback/')  # Build callback URL
                account_reference = f"Unit{unit.unit_number}"  # Set account reference
                transaction_desc = f"Rent payment for {unit.property.name}"  # Set transaction description
                mpesa_response = stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)  # Initiate Mpesa STK push
                transaction_code = mpesa_response.get('CheckoutRequestID', '')  # Get transaction code
                Payment.objects.create(
                    lease=lease,  # Assign lease
                    amount=amount,  # Set amount
                    payment_date=timezone.now(),  # Set payment date
                    payment_method='mpesa',  # Set payment method
                    transaction_code=transaction_code,  # Set transaction code
                    is_confirmed=False  # Mark as unconfirmed
                )
                send_mail(
                    subject="Rent Payment Receipt",  # Email subject
                    message=f"Thank you for your payment of ${amount} for unit {unit.unit_number} at {unit.property.name}.",  # Email message
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Sender email
                    recipient_list=[user.email],  # Recipient email
                    fail_silently=True,  # Fail silently
                )
                return redirect('users:tenant_profile')  # Redirect to tenant profile
            except Exception:
                pass  # Ignore errors
    return render(request, 'payments/lipa_na_mpesa.html', {'amount': amount})  # Render Mpesa payment template

def card_payment(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()  # Get active lease
    unit = lease.unit if lease else None  # Get unit from lease
    amount = request.POST.get('amount') or request.GET.get('amount')  # Get amount from POST or GET
    if request.method == 'POST' and 'pay_rent' in request.POST:  # If rent payment form submitted
        card_number = request.POST.get('card_number')  # Get card number
        expiry = request.POST.get('expiry')  # Get card expiry
        cvv = request.POST.get('cvv')  # Get card CVV
        if lease and amount and card_number and expiry and cvv:
            try:
                amount = float(amount)  # Convert amount to float
                # Here you would integrate with a real card processor
                Payment.objects.create(
                    lease=lease,  # Assign lease
                    amount=amount,  # Set amount
                    payment_date=timezone.now(),  # Set payment date
                    payment_method='card',  # Set payment method
                    transaction_code=card_number[-4:],  # Store last 4 digits for reference
                    is_confirmed=True  # Simulate instant confirmation
                )
                send_mail(
                    subject="Rent Payment Receipt",  # Email subject
                    message=f"Thank you for your card payment of ${amount} for unit {unit.unit_number} at {unit.property.name}.",  # Email message
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Sender email
                    recipient_list=[user.email],  # Recipient email
                    fail_silently=True,  # Fail silently
                )
                return redirect('users:tenant_profile')  # Redirect to tenant profile
            except Exception:
                pass  # Ignore errors
    return render(request, 'payments/card_payment.html', {'amount': amount})  # Render card payment template

def bank_transfer(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()  # Get active lease
    unit = lease.unit if lease else None  # Get unit from lease
    amount = request.POST.get('amount') or request.GET.get('amount')  # Get amount from POST or GET
    if request.method == 'POST' and 'pay_rent' in request.POST:  # If rent payment form submitted
        bank_name = request.POST.get('bank_name')  # Get bank name
        account_number = request.POST.get('account_number')  # Get account number
        transaction_reference = request.POST.get('transaction_reference')  # Get transaction reference
        if lease and amount and bank_name and account_number and transaction_reference:
            try:
                amount = float(amount)  # Convert amount to float
                Payment.objects.create(
                    lease=lease,  # Assign lease
                    amount=amount,  # Set amount
                    payment_date=timezone.now(),  # Set payment date
                    payment_method='bank',  # Set payment method
                    transaction_code=transaction_reference,  # Set transaction code
                    is_confirmed=True  # Simulate instant confirmation
                )
                send_mail(
                    subject="Rent Payment Receipt",  # Email subject
                    message=f"Thank you for your bank transfer of ${amount} for unit {unit.unit_number} at {unit.property.name}.",  # Email message
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Sender email
                    recipient_list=[user.email],  # Recipient email
                    fail_silently=True,  # Fail silently
                )
                return redirect('users:tenant_profile')  # Redirect to tenant profile
            except Exception:
                pass  # Ignore errors
    return render(request, 'payments/bank_transfer.html', {'amount': amount})  # Render bank transfer template

@csrf_exempt  # Exempt from CSRF protection (for external callbacks)
def mpesa_callback(request):
    if request.method == 'POST':  # If POST request
        data = json.loads(request.body.decode('utf-8'))  # Parse JSON body
        # You can log or process the callback data here
        # For now, just return a success response
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})  # Return success response
    return JsonResponse({"error": "Invalid request"}, status=400)  # Return error for non-POST requests
