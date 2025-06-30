from django.db import models
from properties.models import Lease
from users.models import User

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card Transaction'),
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    transaction_code = models.CharField(max_length=50, blank=True, null=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    receipt_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.lease}"