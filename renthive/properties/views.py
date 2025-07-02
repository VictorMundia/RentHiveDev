from users.models_bank import OwnerBankAccount  # Import OwnerBankAccount model from users app
from django.contrib import messages  # Import messages framework for user notifications
from django.urls import reverse  # Import reverse for URL resolution
from django.contrib.auth.decorators import login_required  # Import decorator to require login
from django.shortcuts import render, get_object_or_404, redirect  # Import shortcuts for rendering and redirects

from .models import Property, Unit  # Import Property and Unit models from current app
from .forms import PropertyForm, UnitForm, TenantInviteForm  # Import forms for property, unit, and tenant invite
from payments.models import Payment  # Import Payment model from payments app
from maintenance.models import MaintenanceRequest  # Import MaintenanceRequest model from maintenance app
from django.db.models import Sum  # Import Sum aggregation function
from django.core.mail import send_mail, EmailMessage  # Import email sending utilities

@login_required  # Require user to be logged in
def property_create(request):  # View to create a property
    if request.user.user_type == 'owner':  # Check if user is an owner
        if not hasattr(request.user, 'bank_account'):  # Check if owner has bank account details
            messages.warning(request, "Please add your bank/account details before adding a property.")  # Warn user
            return redirect('users:owner_bank_details')  # Redirect to bank details page
    # ...existing property creation logic...
    # You will need to insert the rest of your property creation logic here

from django.contrib.auth.decorators import login_required  # (Duplicate) Import login_required decorator
from django.shortcuts import render, get_object_or_404, redirect  # (Duplicate) Import shortcuts
from django.contrib import messages  # (Duplicate) Import messages
from .models import Property, Unit  # (Duplicate) Import models
from .forms import PropertyForm, UnitForm, TenantInviteForm  # (Duplicate) Import forms
from payments.models import Payment  # (Duplicate) Import Payment model
from maintenance.models import MaintenanceRequest  # (Duplicate) Import MaintenanceRequest model
from django.db.models import Sum  # (Duplicate) Import Sum
from django.core.mail import send_mail, EmailMessage  # (Duplicate) Import email utilities
from django.conf import settings  # Import settings for email configuration

@login_required  # Require login
def property_list(request):  # View to list properties for the owner
    properties = Property.objects.filter(owner=request.user)  # Get properties owned by user
    property_stats = []  # Initialize list for property statistics
    for prop in properties:  # Loop through each property
        units = prop.units.all()  # Get all units for the property
        vacant_units = units.filter(status='vacant').count()  # Count vacant units
        occupied_units = units.filter(status='occupied').count()  # Count occupied units
        paid_units = unpaid_units = 0  # Initialize paid/unpaid unit counters
        total_rent_paid = 0  # Initialize total rent paid
        for unit in units:  # Loop through each unit
            lease = unit.leases.filter(is_active=True).first()  # Get active lease for unit
            if lease:  # If lease exists
                payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()  # Get latest confirmed payment
                if payment:  # If payment exists
                    paid_units += 1  # Increment paid units
                    total_rent_paid += payment.amount  # Add payment amount to total
                else:
                    unpaid_units += 1  # Increment unpaid units
        maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()  # Count maintenance requests for units
        property_stats.append({  # Add property stats to list
            'property': prop,
            'vacant_units': vacant_units,
            'occupied_units': occupied_units,
            'paid_units': paid_units,
            'unpaid_units': unpaid_units,
            'maintenance_requests': maintenance_requests,
            'total_rent_paid': total_rent_paid,
        })
    return render(request, 'properties/property_list.html', {'property_stats': property_stats})  # Render property list template

@login_required  # Require login
def property_detail(request, pk):  # View to show property details
    property = get_object_or_404(Property, pk=pk, owner=request.user)  # Get property by pk and owner
    units = property.units.all()  # Get all units for property
    vacant_units = units.filter(status='vacant').count()  # Count vacant units
    occupied_units = units.filter(status='occupied').count()  # Count occupied units
    paid_units = unpaid_units = 0  # Initialize counters
    total_rent_paid = 0  # Initialize total rent paid
    for unit in units:  # Loop through units
        lease = unit.leases.filter(is_active=True).first()  # Get active lease
        if lease:  # If lease exists
            payment = Payment.objects.filter(lease=lease, is_confirmed=True).order_by('-payment_date').first()  # Get latest payment
            if payment:  # If payment exists
                paid_units += 1  # Increment paid units
                total_rent_paid += payment.amount  # Add to total rent paid
            else:
                unpaid_units += 1  # Increment unpaid units
    maintenance_requests = MaintenanceRequest.objects.filter(unit__in=units).count()  # Count maintenance requests
    return render(request, 'properties/property_detail.html', {  # Render property detail template
        'property': property,
        'units': units,
        'vacant_units': vacant_units,
        'occupied_units': occupied_units,
        'paid_units': paid_units,
        'unpaid_units': unpaid_units,
        'maintenance_requests': maintenance_requests,
        'total_rent_paid': total_rent_paid,
    })

@login_required  # Require login
def property_create(request):  # View to create a property
    if request.method == 'POST':  # If form submitted
        form = PropertyForm(request.POST)  # Bind form with POST data
        if form.is_valid():  # If form is valid
            property = form.save(commit=False)  # Create property object but don't save yet
            property.owner = request.user  # Set owner to current user
            property.save()  # Save property
            # Do NOT auto-create units. Owner will add units manually later.
            messages.success(request, 'Property created successfully!')  # Show success message
            return redirect('properties:property_list')  # Redirect to property list
    else:
        form = PropertyForm()  # Create empty form
    return render(request, 'properties/property_form.html', {'form': form})  # Render property form template

@login_required  # Require login
def property_update(request, pk):  # View to update a property
    property = get_object_or_404(Property, pk=pk, owner=request.user)  # Get property by pk and owner
    if request.method == 'POST':  # If form submitted
        form = PropertyForm(request.POST, instance=property)  # Bind form with POST data and property instance
        if form.is_valid():  # If form is valid
            form.save()  # Save changes
            messages.success(request, 'Property updated successfully!')  # Show success message
            return redirect('properties:property_list')  # Redirect to property list
    else:
        form = PropertyForm(instance=property)  # Create form with property instance
    return render(request, 'properties/property_form.html', {'form': form})  # Render property form template

@login_required  # Require login
def property_delete(request, pk):  # View to delete a property
    property = get_object_or_404(Property, pk=pk, owner=request.user)  # Get property by pk and owner
    if request.method == 'POST':  # If form submitted
        property.delete()  # Delete property
        messages.success(request, 'Property deleted successfully!')  # Show success message
        return redirect('properties:property_list')  # Redirect to property list
    return render(request, 'properties/property_confirm_delete.html', {'property': property})  # Render confirm delete template

@login_required  # Require login
def invite_tenant(request, unit_id):  # View to invite a tenant to a unit
    unit = get_object_or_404(Unit, pk=unit_id, property__owner=request.user)  # Get unit by id and owner
    if request.method == 'POST':  # If form submitted
        form = TenantInviteForm(request.POST)  # Bind form with POST data
        if form.is_valid():  # If form is valid
            email = form.cleaned_data['email']  # Get email from form
            message = form.cleaned_data['message']  # Get message from form
            # Generate a unique invite link (stub for now)
            invite_link = request.build_absolute_uri(f"/users/register/?unit={unit.pk}")  # Build invite link
            email_body = f"You have been invited to join unit {unit.unit_number} at {unit.property.name}.\n\n"  # Email body
            if message:
                email_body += f"Message from owner: {message}\n\n"  # Add owner's message
            email_body += f"Register here: {invite_link}"  # Add invite link
            send_mail(
                subject="You're invited to join a property on RentHive",  # Email subject
                message=email_body,  # Email body
                from_email=request.user.email,  # Use the owner's email as the sender
                recipient_list=[email],  # Recipient email
                fail_silently=False,  # Raise errors if any
            )
            messages.success(request, f"Invitation sent to {email}!")  # Show success message
            return redirect('properties:property_detail', pk=unit.property.pk)  # Redirect to property detail
    else:
        form = TenantInviteForm()  # Create empty form
    return render(request, 'properties/invite_tenant.html', {'form': form, 'unit': unit})  # Render invite tenant template

@login_required  # Require login
def invite_tenant_property(request, pk):  # View to invite a tenant to a property (assigns to vacant unit)
    property = get_object_or_404(Property, pk=pk, owner=request.user)  # Get property by pk and owner
    if request.method == 'POST':  # If form submitted
        form = TenantInviteForm(request.POST)  # Bind form with POST data
        if form.is_valid():  # If form is valid
            email = form.cleaned_data['email']  # Get email from form
            message = form.cleaned_data['message']  # Get message from form
            vacant_unit = property.units.filter(status='vacant').first()  # Get first vacant unit
            if not vacant_unit:  # If no vacant unit
                messages.error(request, 'No vacant units available in this property.')  # Show error message
            else:
                vacant_unit.status = 'occupied'  # Mark unit as occupied
                vacant_unit.save()  # Save unit
                invite_link = request.build_absolute_uri(f"/users/register/?unit={vacant_unit.pk}")  # Build invite link
                email_body = (
                    f"Hello!\n\n"
                    f"You have been invited to become a tenant at '{property.name}'.\n"
                    f"Property Location: {property.location}\n"
                    f"You will be assigned to Unit {vacant_unit.unit_number}.\n\n"
                )
                if message:
                    email_body += f"Message from the property owner:\n{message}\n\n"  # Add owner's message
                email_body += (
                    "To complete your registration and move-in, please click the link below:\n"
                    f"{invite_link}\n\n"
                    "If you have any questions, simply reply to this email.\n\n"
                    "Welcome to your new home!\n"
                    "- The RentHive Team"
                )
                # Use authenticated email as sender, owner's email as reply-to
                mail = EmailMessage(
                    subject="You're invited to join a property on RentHive",  # Email subject
                    body=email_body,  # Email body
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Default sender email
                    to=[email],  # Recipient email
                    reply_to=[request.user.email]  # Owner's email as reply-to
                )
                mail.send(fail_silently=False)  # Send email
                messages.success(request, f"Invitation sent to {email}! The tenant will be assigned to unit {vacant_unit.unit_number}.")  # Show success message
                return redirect('properties:property_detail', pk=property.pk)  # Redirect to property detail
    else:
        form = TenantInviteForm()  # Create empty form
    return render(request, 'properties/invite_tenant_property.html', {'form': form, 'property': property})  # Render invite tenant property template

@login_required  # Require login
def add_unit(request, property_pk):  # View to add a unit to a property
    property = get_object_or_404(Property, pk=property_pk, owner=request.user)  # Get property by pk and owner
    if request.method == 'POST':  # If form submitted
        form = UnitForm(request.POST)  # Bind form with POST data
        if form.is_valid():  # If form is valid
            unit = form.save(commit=False)  # Create unit object but don't save yet
            unit.property = property  # Assign property to unit
            unit.save()  # Save unit
            messages.success(request, 'Unit added successfully!')  # Show success message
            return redirect('properties:property_detail', pk=property.pk)  # Redirect to property detail
    else:
        form = UnitForm()  # Create empty form
    return render(request, 'properties/unit_form.html', {'form': form, 'property': property})  # Render unit form template

@login_required  # Require login
def unit_detail(request, unit_id):  # View to show unit details
    unit = get_object_or_404(Unit, pk=unit_id, property__owner=request.user)  # Get unit by id and owner
    lease = unit.leases.filter(is_active=True).first()  # Get active lease for unit
    tenant = lease.tenant if lease else None  # Get tenant if lease exists
    payments = Payment.objects.filter(lease=lease).order_by('-payment_date') if lease else []  # Get payments for lease
    maintenance_requests = MaintenanceRequest.objects.filter(unit=unit).order_by('-created_at')  # Get maintenance requests for unit
    rent_balance = 0  # Initialize rent balance
    if lease:  # If lease exists
        total_paid = payments.filter(is_confirmed=True).aggregate(total=Sum('amount'))['total'] or 0  # Sum confirmed payments
        rent_balance = lease.rent_amount - total_paid  # Calculate rent balance
    return render(request, 'properties/unit_detail.html', {  # Render unit detail template
        'unit': unit,
        'tenant': tenant,
        'lease': lease,
        'payments': payments,
        'maintenance_requests': maintenance_requests,
        'rent_balance': rent_balance,
    })