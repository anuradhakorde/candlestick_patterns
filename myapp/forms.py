from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class UserCreateForm(UserCreationForm):
    """
    Form for creating new users with additional fields.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1-555-0000'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Staff status',
        help_text='Designates whether the user can log into the admin site.'
    )
    is_superuser = forms.BooleanField(
        required=False,
        label='Superuser status',
        help_text='Designates that this user has all permissions without explicitly assigning them.'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'password1', 'password2', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
            if not phone_pattern.match(phone_number):
                raise ValidationError("Enter a valid phone number (e.g., +1-555-0000 or (555) 123-4567)")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """
    Form for editing existing users.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1-555-0000'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        label='Active',
        help_text='Designates whether this user should be treated as active.'
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Staff status',
        help_text='Designates whether the user can log into the admin site.'
    )
    is_superuser = forms.BooleanField(
        required=False,
        label='Superuser status',
        help_text='Designates that this user has all permissions without explicitly assigning them.'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username read-only for existing users
        if self.instance and self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['username'].help_text = "Username cannot be changed for existing users."

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email is already used by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
            if not phone_pattern.match(phone_number):
                raise ValidationError("Enter a valid phone number (e.g., +1-555-0000 or (555) 123-4567)")
        return phone_number


class UserPasswordChangeForm(forms.Form):
    """
    Form for changing user passwords by admin.
    """
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text="Your password must contain at least 8 characters."
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        help_text="Enter the same password as before, for verification."
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user