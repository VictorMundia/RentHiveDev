from django.contrib.auth.decorators import login_required  # Decorator to require login for views
from django.shortcuts import render, get_object_or_404, redirect  # Utilities for rendering templates and redirects
from .models import MaintenanceChat, MaintenanceMessage, MaintenanceRequest  # Import models from current app
from .forms import MaintenanceRequestForm  # Import form for maintenance requests
from properties.models import Lease, Unit  # Import Lease and Unit models from properties app
from users.models import User, Notification  # Import User and Notification models from users app
from django.utils import timezone  # Utility for timezone-aware datetimes
from django.core.mail import send_mail  # Function to send emails
from django.conf import settings  # Access Django settings
import csv  # CSV module for report export
from django.http import HttpResponse  # HTTP response class

# Create your views here.
@login_required  # Require user to be logged in
def create_request(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()  # Get active lease for user
    unit = lease.unit if lease else None  # Get unit from lease if exists
    if request.method == 'POST':  # If form is submitted
        form = MaintenanceRequestForm(request.POST)  # Bind form with POST data
        if form.is_valid():  # Validate form
            req = form.save(commit=False)  # Create request object but don't save yet
            if not unit:  # If no unit found
                form.add_error(None, 'No active lease/unit found. Please contact your property owner.')  # Add error
            else:
                req.unit = unit  # Assign unit to request
                req.requested_by = user  # Assign user as requester
                req.save()  # Save request
                # Redirect to tenant requests list after submission
                return redirect('maintenance:tenant_requests_list')  # Redirect to list
    else:
        form = MaintenanceRequestForm()  # Create empty form for GET
    return render(request, 'maintenance/create_request.html', {'form': form})  # Render form template

@login_required  # Require login
def maintenance_chat(request):
    user = request.user  # Get current user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()  # Get active lease
    unit = lease.unit if lease else None  # Get unit from lease
    if not unit:  # If no unit, redirect to profile
        return redirect('users:tenant_profile')
    chat, created = MaintenanceChat.objects.get_or_create(unit=unit, tenant=user)  # Get or create chat for unit/tenant
    if request.method == 'POST':  # If message sent
        message = request.POST.get('message')  # Get message from POST
        if message:  # If message not empty
            MaintenanceMessage.objects.create(chat=chat, sender=user, message=message, timestamp=timezone.now())  # Save message
            # Email alert to property owner (HTML)
            owner = unit.property.owner  # Get property owner
            owner_email = owner.email  # Get owner's email
            subject = f"🛠️ New Maintenance Request from {user.get_full_name() or user.username}"  # Email subject
            dashboard_url = f"{request.scheme}://{request.get_host()}/maintenance/owner/requests/"  # Dashboard URL
            html_message = f"""  # HTML email content
                <h2 style='color:#FFD600;'>New Maintenance Request</h2>
                <p><strong>Tenant:</strong> {user.get_full_name() or user.username} ({user.email})</p>
                <p><strong>Unit:</strong> {unit.property.name} - {unit.unit_number}</p>
                <p><strong>Message:</strong> {message}</p>
                <p><a href='{dashboard_url}' style='background:#FFD600;color:#000;padding:10px 20px;border-radius:5px;text-decoration:none;'>View All Requests</a></p>
            """
            send_mail(
                subject=subject,  # Email subject
                message=f"{user.get_full_name() or user.username} sent a new maintenance request for unit {unit.unit_number}: {message}",  # Plain text message
                from_email=settings.DEFAULT_FROM_EMAIL,  # Sender email
                recipient_list=[owner_email],  # Recipient list
                html_message=html_message,  # HTML message
                fail_silently=True,  # Don't raise errors
            )
            # In-app notification
            Notification.objects.create(
                user=owner,  # Notify owner
                message=f"New maintenance request from {user.get_full_name() or user.username} for {unit.property.name} - {unit.unit_number}",  # Notification message
                url="/maintenance/owner/requests/"  # Link to requests
            )
            return redirect('maintenance:chat')  # Refresh chat page
    messages = chat.messages.order_by('timestamp')  # Get all messages in chat
    return render(request, 'maintenance/chat.html', {'chat': chat, 'messages': messages, 'unit': unit})  # Render chat template

@login_required  # Require login
def owner_maintenance_chats(request):
    # Get all chats for units owned by the current owner
    units = Unit.objects.filter(property__owner=request.user)  # Get units owned by user
    chats = MaintenanceChat.objects.filter(unit__in=units).select_related('tenant', 'unit').order_by('-created_at')  # Get chats for those units
    return render(request, 'maintenance/owner_chats.html', {'chats': chats})  # Render owner chats template

@login_required  # Require login
def owner_maintenance_chat_detail(request, chat_id):
    chat = get_object_or_404(MaintenanceChat, pk=chat_id, unit__property__owner=request.user)  # Get chat or 404 if not owned
    if request.method == 'POST':  # If message sent
        message = request.POST.get('message')  # Get message
        if message:  # If not empty
            MaintenanceMessage.objects.create(chat=chat, sender=request.user, message=message, timestamp=timezone.now())  # Save message
            # Email alert to tenant
            tenant_email = chat.tenant.email  # Get tenant email
            send_mail(
                subject=f"New Maintenance Response from {request.user.get_full_name() or request.user.username}",  # Subject
                message=f"{request.user.get_full_name() or request.user.username} responded to your maintenance request for unit {chat.unit.unit_number}:\n\n{message}",  # Message
                from_email=settings.DEFAULT_FROM_EMAIL,  # Sender
                recipient_list=[tenant_email],  # Recipient
                fail_silently=True,  # Don't raise errors
            )
            return redirect('maintenance:owner_chat_detail', chat_id=chat.id)  # Refresh chat detail
    messages = chat.messages.order_by('timestamp')  # Get messages
    return render(request, 'maintenance/owner_chat_detail.html', {'chat': chat, 'messages': messages})  # Render chat detail

@login_required  # Require login
def owner_requests_dashboard(request):
    if not request.user.user_type == 'owner':  # Only owners allowed
        return redirect('users:dashboard')  # Redirect if not owner
    units = Unit.objects.filter(property__owner=request.user)  # Get units owned
    requests = MaintenanceRequest.objects.filter(unit__in=units).order_by('-created_at')  # Get requests for those units
    if request.method == 'POST':  # If form submitted
        req_id = request.POST.get('request_id')  # Get request ID
        action = request.POST.get('action')  # Get action type
        assigned_to = request.POST.get('assigned_to')  # Get assigned to
        req = MaintenanceRequest.objects.get(id=req_id)  # Get request object
        if action == 'update_status':  # If updating status
            req.status = request.POST.get('status')  # Set new status
            req.save()  # Save
        if action == 'assign' and assigned_to:  # If assigning
            req.assigned_to = assigned_to  # Set assigned to
            req.save()  # Save
        if action == 'mark_resolved':  # If marking as resolved
            req.status = 'completed'  # Set status to completed
            req.save()  # Save
        # Optionally: notify tenant of status change
    return render(request, 'maintenance/owner_requests_dashboard.html', {'requests': requests})  # Render dashboard

@login_required  # Require login
def confirm_maintenance_resolution(request, req_id):
    req = get_object_or_404(MaintenanceRequest, id=req_id, requested_by=request.user)  # Get request or 404 if not owned
    if request.method == 'POST':  # If form submitted
        req.tenant_confirmed = True  # Mark as confirmed by tenant
        req.feedback_rating = int(request.POST.get('feedback_rating', 5))  # Get feedback rating, default 5
        req.tenant_feedback = request.POST.get('tenant_feedback', '')  # Get feedback text
        req.save()  # Save
        return render(request, 'maintenance/confirmation_thankyou.html', {'request_obj': req})  # Thank you page
    return render(request, 'maintenance/confirm_resolution.html', {'request_obj': req})  # Render confirmation form

@login_required  # Require login
def tenant_requests_list(request):
    requests = MaintenanceRequest.objects.filter(requested_by=request.user).order_by('-created_at')  # Get requests by user
    return render(request, 'maintenance/tenant_requests_list.html', {'requests': requests})  # Render list

@login_required  # Require login
def maintenance_report_csv(request):
    if not request.user.user_type == 'owner':  # Only owners allowed
        return redirect('users:dashboard')  # Redirect if not owner
    units = Unit.objects.filter(property__owner=request.user)  # Get units owned
    requests_qs = MaintenanceRequest.objects.filter(unit__in=units).order_by('-created_at')  # Get requests for those units
    response = HttpResponse(content_type='text/csv')  # Create CSV response
    response['Content-Disposition'] = 'attachment; filename="maintenance_report.csv"'  # Set filename
    writer = csv.writer(response)  # Create CSV writer
    writer.writerow(['Date', 'Property', 'Unit', 'Issue', 'Priority', 'Status', 'Assigned To', 'Resolved By', 'Tenant Confirmed', 'Feedback', 'Rating'])  # Write header
    for req in requests_qs:  # For each request
        writer.writerow([
            req.created_at.strftime('%Y-%m-%d %H:%M'),  # Date
            req.unit.property.name,  # Property name
            req.unit.unit_number,  # Unit number
            req.issue,  # Issue description
            req.get_priority_display(),  # Priority (display value)
            req.get_status_display(),  # Status (display value)
            req.assigned_to or '',  # Assigned to
            req.resolved_by.get_full_name() if req.resolved_by else '',  # Resolved by
            'Yes' if req.tenant_confirmed else 'No',  # Tenant confirmed
            req.tenant_feedback or '',  # Feedback
            req.feedback_rating or ''  # Rating
        ])
    return response  # Return CSV file
