from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MaintenanceChat, MaintenanceMessage, MaintenanceRequest
from .forms import MaintenanceRequestForm
from properties.models import Lease, Unit
from users.models import User, Notification
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
@login_required
def create_request(request):
    user = request.user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()
    unit = lease.unit if lease else None
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            if not unit:
                form.add_error(None, 'No active lease/unit found. Please contact your property owner.')
            else:
                req.unit = unit
                req.requested_by = user
                req.save()
                # Redirect to tenant requests list after submission
                return redirect('maintenance:tenant_requests_list')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'maintenance/create_request.html', {'form': form})

@login_required
def maintenance_chat(request):
    user = request.user
    lease = Lease.objects.filter(tenant=user, is_active=True).first()
    unit = lease.unit if lease else None
    if not unit:
        return redirect('users:tenant_profile')
    chat, created = MaintenanceChat.objects.get_or_create(unit=unit, tenant=user)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            MaintenanceMessage.objects.create(chat=chat, sender=user, message=message, timestamp=timezone.now())
            # Email alert to property owner (HTML)
            owner = unit.property.owner
            owner_email = owner.email
            subject = f"🛠️ New Maintenance Request from {user.get_full_name() or user.username}"
            dashboard_url = f"{request.scheme}://{request.get_host()}/maintenance/owner/requests/"
            html_message = f"""
                <h2 style='color:#FFD600;'>New Maintenance Request</h2>
                <p><strong>Tenant:</strong> {user.get_full_name() or user.username} ({user.email})</p>
                <p><strong>Unit:</strong> {unit.property.name} - {unit.unit_number}</p>
                <p><strong>Message:</strong> {message}</p>
                <p><a href='{dashboard_url}' style='background:#FFD600;color:#000;padding:10px 20px;border-radius:5px;text-decoration:none;'>View All Requests</a></p>
            """
            send_mail(
                subject=subject,
                message=f"{user.get_full_name() or user.username} sent a new maintenance request for unit {unit.unit_number}: {message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[owner_email],
                html_message=html_message,
                fail_silently=True,
            )
            # In-app notification
            Notification.objects.create(
                user=owner,
                message=f"New maintenance request from {user.get_full_name() or user.username} for {unit.property.name} - {unit.unit_number}",
                url="/maintenance/owner/requests/"
            )
            return redirect('maintenance:chat')
    messages = chat.messages.order_by('timestamp')
    return render(request, 'maintenance/chat.html', {'chat': chat, 'messages': messages, 'unit': unit})

@login_required
def owner_maintenance_chats(request):
    # Get all chats for units owned by the current owner
    units = Unit.objects.filter(property__owner=request.user)
    chats = MaintenanceChat.objects.filter(unit__in=units).select_related('tenant', 'unit').order_by('-created_at')
    return render(request, 'maintenance/owner_chats.html', {'chats': chats})

@login_required
def owner_maintenance_chat_detail(request, chat_id):
    chat = get_object_or_404(MaintenanceChat, pk=chat_id, unit__property__owner=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            MaintenanceMessage.objects.create(chat=chat, sender=request.user, message=message, timestamp=timezone.now())
            # Email alert to tenant
            tenant_email = chat.tenant.email
            send_mail(
                subject=f"New Maintenance Response from {request.user.get_full_name() or request.user.username}",
                message=f"{request.user.get_full_name() or request.user.username} responded to your maintenance request for unit {chat.unit.unit_number}:\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant_email],
                fail_silently=True,
            )
            return redirect('maintenance:owner_chat_detail', chat_id=chat.id)
    messages = chat.messages.order_by('timestamp')
    return render(request, 'maintenance/owner_chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def owner_requests_dashboard(request):
    if not request.user.user_type == 'owner':
        return redirect('users:dashboard')
    units = Unit.objects.filter(property__owner=request.user)
    requests = MaintenanceRequest.objects.filter(unit__in=units).order_by('-created_at')
    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')
        assigned_to = request.POST.get('assigned_to')
        req = MaintenanceRequest.objects.get(id=req_id)
        if action == 'update_status':
            req.status = request.POST.get('status')
            req.save()
        if action == 'assign' and assigned_to:
            req.assigned_to = assigned_to
            req.save()
        if action == 'mark_resolved':
            req.status = 'completed'
            req.save()
        # Optionally: notify tenant of status change
    return render(request, 'maintenance/owner_requests_dashboard.html', {'requests': requests})

@login_required
def confirm_maintenance_resolution(request, req_id):
    req = get_object_or_404(MaintenanceRequest, id=req_id, requested_by=request.user)
    if request.method == 'POST':
        req.tenant_confirmed = True
        req.feedback_rating = int(request.POST.get('feedback_rating', 5))
        req.tenant_feedback = request.POST.get('tenant_feedback', '')
        req.save()
        return render(request, 'maintenance/confirmation_thankyou.html', {'request_obj': req})
    return render(request, 'maintenance/confirm_resolution.html', {'request_obj': req})

@login_required
def tenant_requests_list(request):
    requests = MaintenanceRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'maintenance/tenant_requests_list.html', {'requests': requests})
