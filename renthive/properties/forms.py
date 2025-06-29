from django import forms
from .models import Property, Unit

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'location', 'description', 'unit_count']

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'bedrooms', 'rent_amount', 'status']

class TenantInviteForm(forms.Form):
    email = forms.EmailField(label="Tenant's Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label="Message (optional)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
