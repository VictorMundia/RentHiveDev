from django.db import models  # Import Django's models module for ORM support
from properties.models import Unit  # Import the Unit model from the properties app
from users.models import User  # Import the User model from the users app

class MaintenanceRequest(models.Model):  # Model representing a maintenance request
    PRIORITY_CHOICES = [  # Choices for the priority field
        ('low', 'Low'),  # Low priority
        ('medium', 'Medium'),  # Medium priority
        ('high', 'High'),  # High priority
        ('emergency', 'Emergency'),  # Emergency priority
    ]
    
    STATUS_CHOICES = [  # Choices for the status field
        ('pending', 'Pending'),  # Request is pending
        ('in_progress', 'In Progress'),  # Request is being worked on
        ('completed', 'Completed'),  # Request is completed
    ]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='maintenance_requests')  # Link to the Unit needing maintenance
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')  # User who made the request
    issue = models.TextField()  # Description of the maintenance issue
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')  # Priority of the request
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')  # Current status of the request
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the request was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the request was last updated
    resolved_at = models.DateTimeField(null=True, blank=True)  # Timestamp when the request was resolved
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_requests')  # User who resolved the request
    assigned_to = models.CharField(max_length=100, blank=True, null=True, help_text='Contractor or person assigned')  # Name of the person or contractor assigned
    tenant_confirmed = models.BooleanField(default=False)  # Whether the tenant confirmed the resolution
    tenant_feedback = models.TextField(blank=True, null=True)  # Feedback from the tenant
    feedback_rating = models.PositiveSmallIntegerField(blank=True, null=True, help_text='1-5 stars')  # Tenant's rating (1-5 stars)
    
    def __str__(self):  # String representation of the object
        return f"Maintenance for {self.unit} - {self.get_status_display()}"  # Display unit and status

class MaintenanceChat(models.Model):  # Model representing a chat related to maintenance
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='chats')  # Unit associated with the chat
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_chats')  # Tenant participating in the chat
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the chat was created

class MaintenanceMessage(models.Model):  # Model representing a message in a maintenance chat
    chat = models.ForeignKey(MaintenanceChat, on_delete=models.CASCADE, related_name='messages')  # Chat to which the message belongs
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # User who sent the message
    message = models.TextField()  # Content of the message
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp when the message was sent