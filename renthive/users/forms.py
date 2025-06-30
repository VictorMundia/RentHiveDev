from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User

class RegisterForm(UserCreationForm):
    id_number = forms.CharField(max_length=20, required=True, label="ID Number")
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'id_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['user_type'].empty_label = 'Select user type'
