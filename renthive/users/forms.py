from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from users.models_bank import OwnerBankAccount
class OwnerBankAccountForm(forms.ModelForm):
    class Meta:
        model = OwnerBankAccount
        fields = ['bank_name', 'account_number', 'account_name', 'branch']
from users.models_bank import OwnerBankAccount
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
class OwnerBankAccountForm(forms.ModelForm):
    class Meta:

        model = OwnerBankAccount
        fields = ['bank_name', 'account_number', 'account_name', 'branch']

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
        # The code above defines Django forms for user registration and owner bank account details.

        # Import the Django forms module.
        # Import the built-in UserCreationForm for user registration.
        # Import the custom User model from the users app.
        # Import the OwnerBankAccount model from the users.models_bank module.

        # Define a ModelForm for the OwnerBankAccount model.
        class OwnerBankAccountForm(forms.ModelForm):
            # Specify metadata for the form.
            class Meta:
                # Set the model to OwnerBankAccount.
                model = OwnerBankAccount
                # List the fields to include in the form.
                fields = ['bank_name', 'account_number', 'account_name', 'branch']

        # Import the OwnerBankAccount model again (redundant, can be removed).

        # Define the OwnerBankAccountForm again (duplicate, can be removed).
        class OwnerBankAccountForm(forms.ModelForm):
            class Meta:
                model = OwnerBankAccount
                fields = ['bank_name', 'account_number', 'account_name', 'branch']

        # Define a registration form that extends the built-in UserCreationForm.
        class RegisterForm(UserCreationForm):
            # Add a required CharField for the user's ID number.
            id_number = forms.CharField(max_length=20, required=True, label="ID Number")
            # Add a required CharField for the user's first name.
            first_name = forms.CharField(max_length=30, required=True, label="First Name")
            # Add a required CharField for the user's last name.
            last_name = forms.CharField(max_length=30, required=True, label="Last Name")

            # Specify metadata for the form.
            class Meta:
                # Set the model to the custom User model.
                model = User
                # List the fields to include in the registration form.
                fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'id_number', 'password1', 'password2')

            # Customize the form initialization.
            def __init__(self, *args, **kwargs):
                # Call the parent class's __init__ method.
                super().__init__(*args, **kwargs)
                # Add the 'form-control' CSS class to all form fields for styling.
                for field in self.fields.values():
                    field.widget.attrs['class'] = 'form-control'
                # Set a custom empty label for the user_type dropdown.
                self.fields['user_type'].empty_label = 'Select user type'