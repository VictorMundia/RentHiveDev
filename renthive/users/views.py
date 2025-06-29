from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.models import Lease, Unit
from payments.models import Payment
from maintenance.models import MaintenanceRequest

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