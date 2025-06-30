from django.db import models
from properties.models import Unit
from users.models import User

class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='maintenance_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    issue = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_requests')
    assigned_to = models.CharField(max_length=100, blank=True, null=True, help_text='Contractor or person assigned')
    tenant_confirmed = models.BooleanField(default=False)
    tenant_feedback = models.TextField(blank=True, null=True)
    feedback_rating = models.PositiveSmallIntegerField(blank=True, null=True, help_text='1-5 stars')
    
    def __str__(self):
        return f"Maintenance for {self.unit} - {self.get_status_display()}"

class MaintenanceChat(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='chats')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_chats')
    created_at = models.DateTimeField(auto_now_add=True)

class MaintenanceMessage(models.Model):
    chat = models.ForeignKey(MaintenanceChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)