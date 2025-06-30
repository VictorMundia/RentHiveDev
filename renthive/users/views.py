from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from properties.models import Lease, Unit, Property
from payments.models import Payment
from maintenance.models import MaintenanceRequest
from .forms import RegisterForm
from django.utils import timezone
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

@login_required
def dashboard(request):
    context = {}
    
    if request.user.user_type == 'tenant':
        # Tenant dashboard
        lease = Lease.objects.filter(tenant=request.user, is_active=True).first()
        payments = Payment.objects.filter(lease=lease).order_by('-payment_date')[:5] if lease else []
        maintenance_requests = MaintenanceRequest.objects.filter(requested_by=request.user).order_by('-created_at')[:5]
        
        context.update({
            'lease': lease,
            'payments': payments,
            'maintenance_requests': maintenance_requests,
        })
    elif request.user.user_type == 'owner':
        # Owner dashboard
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
        
        context.update({
            'properties': properties,
            'pending_payments': pending_payments,
            'pending_requests': pending_requests,
        })
    
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    user = request.user
    properties = Property.objects.filter(owner=user)
    total_properties = properties.count()
    selected_property = None
    vacant_units = occupied_units = paid_units = unpaid_units = maintenance_requests = None
    property_id = request.GET.get('property')
    if property_id:
        try:
            selected_property = properties.get(pk=property_id)
            units = selected_property.units.all()
            vacant_units = units.filter(status='vacant').count()
            occupied_units = units.filter(status='occupied').count()
            # Paid and unpaid units (based on latest payment for each unit)
            paid_units = unpaid_units = 0
            for unit in units:
                lease = unit.leases.filter(is_active=True).first()
                if lease:
                    payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()
                    if payment:
                        paid_units += 1
                    else:
                        unpaid_units += 1
            maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()
        except Property.DoesNotExist:
            selected_property = None
    return render(request, 'users/profile.html', {
        'user': user,
        'properties': properties,
        'total_properties': total_properties,
        'selected_property': selected_property,
        'vacant_units': vacant_units,
        'occupied_units': occupied_units,
        'paid_units': paid_units,
        'unpaid_units': unpaid_units,
        'maintenance_requests': maintenance_requests,
    })

def register(request):
    from properties.models import Unit  # Moved import here to avoid circular import issues
    unit_id = request.GET.get('unit')
    invited_unit = None
    if unit_id:
        try:
            invited_unit = Unit.objects.get(pk=unit_id)
        except Unit.DoesNotExist:
            invited_unit = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Save extra fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            # Save ID number to user profile (if you want to store it elsewhere, adjust accordingly)
            # If this is a tenant registering via invite, assign them to the unit and create a lease
            if invited_unit and form.cleaned_data.get('user_type') == 'tenant':
                invited_unit.status = 'occupied'
                invited_unit.save()
                Lease.objects.create(
                    unit=invited_unit,
                    tenant=user,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date().replace(year=timezone.now().year + 1),
                    rent_amount=invited_unit.rent_amount,
                    is_active=True
                )
            login(request, user)
            # Show welcome message with property name
            if invited_unit:
                request.session['welcome_property'] = invited_unit.property.name
            if user.user_type == 'owner':
                return redirect('users:profile')
            else:
                return redirect('users:tenant_profile')
    else:
        form = RegisterForm()
    # Only show errors if the form was submitted (POST)
    show_errors = request.method == 'POST'
    return render(request, 'users/register.html', {'form': form, 'show_errors': show_errors, 'invited_unit': invited_unit})

@login_required
def tenant_profile(request):
    user = request.user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()
    unit = lease.unit if lease else None
    payments = Payment.objects.filter(lease=lease).order_by('-payment_date') if lease else []
    maintenance_requests = MaintenanceRequest.objects.filter(requested_by=user).order_by('-created_at')
    rent_balance = 0
    if lease:
        total_paid = payments.filter(is_confirmed=True).aggregate(total=models.Sum('amount'))['total'] or 0
        rent_balance = lease.rent_amount - total_paid
    # Handle rent payment form
    payment_success = False
    if request.method == 'POST' and 'pay_rent' in request.POST:
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount > 0 and lease:
                payment = Payment.objects.create(
                    lease=lease,
                    amount=amount,
                    payment_date=timezone.now(),
                    is_confirmed=False  # Owner can confirm later
                )
                # Send receipt email
                send_mail(
                    subject="Rent Payment Receipt",
                    message=f"Thank you for your payment of ${amount} for unit {unit.unit_number} at {unit.property.name}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                payment_success = True
        except Exception:
            pass
    return render(request, 'users/tenant_profile.html', {
        'lease': lease,
        'unit': unit,
        'payments': payments,
        'maintenance_requests': maintenance_requests,
        'rent_balance': rent_balance,
        'payment_success': payment_success,
    })