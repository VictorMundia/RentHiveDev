from django import forms  # Import Django's forms module
from django.contrib.auth.forms import UserCreationForm  # Import Django's built-in user creation form
from users.models import User  # Import the custom User model
from users.models_bank import OwnerBankAccount  # Import the OwnerBankAccount model

class OwnerBankAccountForm(forms.ModelForm):  # Define a form for OwnerBankAccount model
    class Meta:  # Meta class to specify model and fields
        model = OwnerBankAccount  # Set the model to OwnerBankAccount
        fields = ['bank_name', 'account_number', 'account_name', 'branch']  # Fields to include in the form

from users.models_bank import OwnerBankAccount  # Duplicate import (can be removed)
from django import forms  # Duplicate import (can be removed)
from django.contrib.auth.forms import UserCreationForm  # Duplicate import (can be removed)
from users.models import User  # Duplicate import (can be removed)

class OwnerBankAccountForm(forms.ModelForm):  # Duplicate form definition (can be removed)
    class Meta:  # Meta class for model and fields
        model = OwnerBankAccount  # Set the model to OwnerBankAccount
        fields = ['bank_name', 'account_number', 'account_name', 'branch']  # Fields to include

class RegisterForm(UserCreationForm):  # Define a registration form extending UserCreationForm
    id_number = forms.CharField(max_length=20, required=True, label="ID Number")  # Add ID number field
    first_name = forms.CharField(max_length=30, required=True, label="First Name")  # Add first name field
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")  # Add last name field

    class Meta:  # Meta class to specify model and fields
        model = User  # Set the model to User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'id_number', 'password1', 'password2')  # Fields to include

    def __init__(self, *args, **kwargs):  # Override the initializer
        super().__init__(*args, **kwargs)  # Call the parent initializer
        self.fields['user_type'].empty_label = 'Select user type'  # Set empty label for user_type field