from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MaintenanceChat, MaintenanceMessage
from properties.models import Lease, Unit
from users.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def create_request(request):
    return render(request, 'maintenance/create_request.html')

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
            # Email alert to property owner
            owner_email = unit.property.owner.email
            send_mail(
                subject=f"New Maintenance Message from {user.get_full_name() or user.username}",
                message=f"{user.get_full_name() or user.username} sent a new message about unit {unit.unit_number}:\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[owner_email],
                fail_silently=True,
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
