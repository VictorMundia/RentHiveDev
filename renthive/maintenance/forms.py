from django import forms
from .models import MaintenanceRequest

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['issue', 'priority']
        widgets = {
            'issue': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded', 'rows': 4, 'placeholder': 'Describe the issue...'}),
            'priority': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
        }
