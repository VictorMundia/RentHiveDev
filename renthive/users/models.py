from django.contrib.auth.models import AbstractUser  # Import Django's built-in abstract user model
from django.db import models  # Import Django's models module for database models

class User(AbstractUser):  # Custom user model extending Django's AbstractUser
    USER_TYPE_CHOICES = (  # Tuple of possible user types
        ('tenant', 'Tenant'),  # Option for tenant user
        ('owner', 'Property Owner'),  # Option for property owner user
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)  # Field to store user type
    phone_number = models.CharField(max_length=15, unique=True)  # Unique phone number for user
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # Optional profile picture
    
    def __str__(self):  # String representation of the user
        return f"{self.get_full_name()} ({self.user_type})"  # Returns full name and user type

class Notification(models.Model):  # Model for notifications
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # Link to user, delete notifications if user is deleted
    message = models.CharField(max_length=255)  # Notification message text
    url = models.URLField(blank=True, null=True)  # Optional URL related to the notification
    is_read = models.BooleanField(default=False)  # Boolean to track if notification is read
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when notification is created

    def __str__(self):  # String representation of the notification
        return f"Notification for {self.user.username}: {self.message[:30]}"  # Shows user and first 30 chars of message
