from django.db import models  # Import Django's models module for ORM support
from users.models import User  # Import the User model from the users app

class Property(models.Model):  # Define the Property model, inheriting from Django's base Model
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')  # Reference to the owner (User), delete properties if user is deleted
    name = models.CharField(max_length=100)  # Name of the property, max 100 characters
    location = models.CharField(max_length=100)  # Location of the property, max 100 characters
    description = models.TextField()  # Detailed description of the property
    unit_count = models.PositiveIntegerField(default=1)  # Number of units in the property, must be positive, default is 1
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the property is created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the property is updated
    
    def __str__(self):  # String representation of the Property object
        return self.name  # Return the property's name

class Unit(models.Model):  # Define the Unit model
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')  # Reference to the Property, delete units if property is deleted
    unit_number = models.CharField(max_length=20)  # Identifier for the unit, max 20 characters
    bedrooms = models.PositiveIntegerField()  # Number of bedrooms in the unit, must be positive
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Rent amount for the unit, up to 10 digits, 2 decimal places
    status = models.CharField(max_length=20, choices=[  # Status of the unit, limited to specified choices
        ('vacant', 'Vacant'),  # Option for vacant unit
        ('occupied', 'Occupied'),  # Option for occupied unit
    ])
    
    def __str__(self):  # String representation of the Unit object
        return f"{self.property.name} - Unit {self.unit_number}"  # Return property name and unit number
    
class Lease(models.Model):  # Define the Lease model
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='leases')  # Reference to the Unit, delete leases if unit is deleted
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leases')  # Reference to the tenant (User), delete leases if user is deleted
    start_date = models.DateField()  # Lease start date
    end_date = models.DateField()  # Lease end date
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Rent amount for the lease, up to 10 digits, 2 decimal places
    is_active = models.BooleanField(default=True)  # Indicates if the lease is currently active, default is True
    
    def __str__(self):  # String representation of the Lease object
        return f"Lease for {self.tenant} at {self.unit}"  # Return tenant and unit information
