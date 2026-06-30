import re

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminStaffForm(forms.Form):
    """Used by Admin to create or edit Branch Manager / Front Desk accounts."""

    ROLE_CHOICES = [
        (User.Role.MANAGER, "Manager"),
        (User.Role.FRONTDESK, "Front Desk"),
    ]

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    branch = forms.ModelChoiceField(queryset=None, required=False, empty_label="Unassigned")
    experience_details = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, require_password=True, **kwargs):
        super().__init__(*args, **kwargs)
        from branches.models import Branch

        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)
        if require_password:
            self.fields["password"].required = True

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class RegisterForm(forms.Form):
    """Matches the Student template's register.html field names."""

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    branch = forms.ModelChoiceField(queryset=None, required=True, empty_label="Select your branch")
    front_desk_user = forms.ModelChoiceField(queryset=None, required=False, empty_label="Auto-assign")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from branches.models import Branch

        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)

        # The front-desk choice depends on whichever branch was submitted.
        self.fields["front_desk_user"].queryset = User.objects.none()
        branch_id = self.data.get("branch") if hasattr(self, "data") else None
        if branch_id:
            self.fields["front_desk_user"].queryset = User.objects.filter(
                role=User.Role.FRONTDESK, branch_id=branch_id, is_active=True
            )

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        if not re.match(r"^[A-Za-z\s\-']+$", value):
            raise forms.ValidationError("First name must contain only letters.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        if not re.match(r"^[A-Za-z\s\-']+$", value):
            raise forms.ValidationError("Last name must contain only letters.")
        return value.title()

    def clean_phone(self):
        value = self.cleaned_data.get("phone", "").strip()
        if value:
            if not re.match(r"^\+?[0-9]{7,15}$", value):
                raise forms.ValidationError("Enter a valid phone number (digits only, 7–15 characters).")
        return value

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class StaffLoginForm(forms.Form):
    """Login form for branch staff (Admin / Manager / Front Desk).

    Includes a role dropdown so staff confirm which dashboard they expect
    to land on; this is cross-checked against the account's actual role.
    """

    ROLE_CHOICES = [
        (User.Role.ADMIN, "Admin"),
        (User.Role.MANAGER, "Manager"),
        (User.Role.FRONTDESK, "Front Desk"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class OTPForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput)
    otp = forms.CharField(max_length=6)
