from django import forms  # Import Django's forms module for creating form classes
from .models import Property, Unit  # Import Property and Unit models from the current app's models

class PropertyForm(forms.ModelForm):  # Define a form for the Property model using ModelForm
    class Meta:  # Meta class to specify model and fields
        model = Property  # Associate this form with the Property model
        fields = ['name', 'location', 'description', 'unit_count']  # Specify fields to include in the form

class UnitForm(forms.ModelForm):  # Define a form for the Unit model using ModelForm
    class Meta:  # Meta class to specify model and fields
        model = Unit  # Associate this form with the Unit model
        fields = ['unit_number', 'bedrooms', 'rent_amount', 'status']  # Specify fields to include in the form

class TenantInviteForm(forms.Form):  # Define a standard form (not tied to a model) for inviting tenants
    email = forms.EmailField(  # Email field for tenant's email address
        label="Tenant's Email",  # Label for the email field
        widget=forms.EmailInput(attrs={'class': 'form-control'})  # Use EmailInput widget with Bootstrap class
    )
    message = forms.CharField(  # CharField for an optional message to the tenant
        label="Message (optional)",  # Label for the message field
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # Use Textarea widget with Bootstrap class and 3 rows
        required=False  # Make this field optional
    )
