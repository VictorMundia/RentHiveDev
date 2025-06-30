from django import forms
from .models import MaintenanceRequest
from properties.models import Unit

class MaintenanceRequestForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=Unit.objects.none(), required=False, label='Unit (if no active lease)', widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}))
    class Meta:
        model = MaintenanceRequest
        fields = ['unit', 'issue', 'priority']
        widgets = {
            'issue': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded', 'rows': 4, 'placeholder': 'Describe the issue...'}),
            'priority': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded'}),
        }
