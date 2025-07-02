from users.models_bank import OwnerBankAccount
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Property, Unit
from .forms import PropertyForm, UnitForm, TenantInviteForm
from payments.models import Payment
from maintenance.models import MaintenanceRequest
from django.db.models import Sum
from django.core.mail import send_mail, EmailMessage

@login_required
def property_create(request):
    if request.user.user_type == 'owner':
        if not hasattr(request.user, 'bank_account'):
            messages.warning(request, "Please add your bank/account details before adding a property.")
            return redirect('users:owner_bank_details')
    # ...existing property creation logic...
    # You will need to insert the rest of your property creation logic here
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, Unit
from .forms import PropertyForm, UnitForm, TenantInviteForm
from payments.models import Payment
from maintenance.models import MaintenanceRequest
from django.db.models import Sum
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

@login_required
def property_list(request):
    properties = Property.objects.filter(owner=request.user)
    property_stats = []
    for prop in properties:
        units = prop.units.all()
        vacant_units = units.filter(status='vacant').count()
        occupied_units = units.filter(status='occupied').count()
        paid_units = unpaid_units = 0
        total_rent_paid = 0
        for unit in units:
            lease = unit.leases.filter(is_active=True).first()
            if lease:
                payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()
                if payment:
                    paid_units += 1
                    total_rent_paid += payment.amount
                else:
                    unpaid_units += 1
        maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()
        property_stats.append({
            'property': prop,
            'vacant_units': vacant_units,
            'occupied_units': occupied_units,
            'paid_units': paid_units,
            'unpaid_units': unpaid_units,
            'maintenance_requests': maintenance_requests,
            'total_rent_paid': total_rent_paid,
        })
    return render(request, 'properties/property_list.html', {'property_stats': property_stats})

@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    units = property.units.all()
    vacant_units = units.filter(status='vacant').count()
    occupied_units = units.filter(status='occupied').count()
    paid_units = unpaid_units = 0
    total_rent_paid = 0
    for unit in units:
        lease = unit.leases.filter(is_active=True).first()
        if lease:
            payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()
            if payment:
                paid_units += 1
                total_rent_paid += payment.amount
            else:
                unpaid_units += 1
    maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()
    return render(request, 'properties/property_detail.html', {
        'property': property,
        'units': units,
        'vacant_units': vacant_units,
        'occupied_units': occupied_units,
        'paid_units': paid_units,
        'unpaid_units': unpaid_units,
        'maintenance_requests': maintenance_requests,
        'total_rent_paid': total_rent_paid,
    })

@login_required
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            # Do NOT auto-create units. Owner will add units manually later.
            messages.success(request, 'Property created successfully!')
            return redirect('properties:property_list')
    else:
        form = PropertyForm()
    return render(request, 'properties/property_form.html', {'form': form})

@login_required
def property_update(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully!')
            return redirect('properties:property_list')
    else:
        form = PropertyForm(instance=property)
    return render(request, 'properties/property_form.html', {'form': form})

@login_required
def property_delete(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('properties:property_list')
    return render(request, 'properties/property_confirm_delete.html', {'property': property})

@login_required
def invite_tenant(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id, property__owner=request.user)
    if request.method == 'POST':
        form = TenantInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Generate a unique invite link (stub for now)
            invite_link = request.build_absolute_uri(f"/users/register/?unit={unit.pk}")
            email_body = f"You have been invited to join unit {unit.unit_number} at {unit.property.name}.\n\n"
            if message:
                email_body += f"Message from owner: {message}\n\n"
            email_body += f"Register here: {invite_link}"
            send_mail(
                subject="You're invited to join a property on RentHive",
                message=email_body,
                from_email=request.user.email,  # Use the owner's email as the sender
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, f"Invitation sent to {email}!")
            return redirect('properties:property_detail', pk=unit.property.pk)
    else:
        form = TenantInviteForm()
    return render(request, 'properties/invite_tenant.html', {'form': form, 'unit': unit})

@login_required
def invite_tenant_property(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TenantInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            vacant_unit = property.units.filter(status='vacant').first()
            if not vacant_unit:
                messages.error(request, 'No vacant units available in this property.')
            else:
                vacant_unit.status = 'occupied'
                vacant_unit.save()
                invite_link = request.build_absolute_uri(f"/users/register/?unit={vacant_unit.pk}")
                email_body = (
                    f"Hello!\n\n"
                    f"You have been invited to become a tenant at '{property.name}'.\n"
                    f"Property Location: {property.location}\n"
                    f"You will be assigned to Unit {vacant_unit.unit_number}.\n\n"
                )
                if message:
                    email_body += f"Message from the property owner:\n{message}\n\n"
                email_body += (
                    "To complete your registration and move-in, please click the link below:\n"
                    f"{invite_link}\n\n"
                    "If you have any questions, simply reply to this email.\n\n"
                    "Welcome to your new home!\n"
                    "- The RentHive Team"
                )
                # Use authenticated email as sender, owner's email as reply-to
                mail = EmailMessage(
                    subject="You're invited to join a property on RentHive",
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                    reply_to=[request.user.email]
                )
                mail.send(fail_silently=False)
                messages.success(request, f"Invitation sent to {email}! The tenant will be assigned to unit {vacant_unit.unit_number}.")
                return redirect('properties:property_detail', pk=property.pk)
    else:
        form = TenantInviteForm()
    return render(request, 'properties/invite_tenant_property.html', {'form': form, 'property': property})

@login_required
def add_unit(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk, owner=request.user)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.property = property
            unit.save()
            messages.success(request, 'Unit added successfully!')
            return redirect('properties:property_detail', pk=property.pk)
    else:
        form = UnitForm()
    return render(request, 'properties/unit_form.html', {'form': form, 'property': property})

@login_required
def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id, property__owner=request.user)
    lease = unit.leases.filter(is_active=True).first()
    tenant = lease.tenant if lease else None
    payments = Payment.objects.filter(lease=lease).order_by('-payment_date') if lease else []
    maintenance_requests = MaintenanceRequest.objects.filter(unit=unit).order_by('-created_at')
    rent_balance = 0
    if lease:
        total_paid = payments.filter(is_confirmed=True).aggregate(total=Sum('amount'))['total'] or 0
        rent_balance = lease.rent_amount - total_paid
    return render(request, 'properties/unit_detail.html', {
        'unit': unit,
        'tenant': tenant,
        'lease': lease,
        'payments': payments,
        'maintenance_requests': maintenance_requests,
        'rent_balance': rent_balance,
    })