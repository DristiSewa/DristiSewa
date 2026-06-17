from django import forms
from django.contrib.auth import get_user_model

from .models import Student

User = get_user_model()


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "date_of_birth",
            "college",
            "passed_year",
            "gpa",
            "test_type",
            "test_score",
            "preferred_country",
            "profile_pic",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "college": forms.TextInput(attrs={"class": "form-input"}),
            "passed_year": forms.NumberInput(attrs={"class": "form-input"}),
            "gpa": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "test_type": forms.Select(attrs={"class": "form-input"}),
            "test_score": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "preferred_country": forms.TextInput(attrs={"class": "form-input"}),
            "profile_pic": forms.FileInput(attrs={"class": "hidden", "accept": "image/*"}),
        }


class StudentRegistrationForm(forms.ModelForm):
    """Used by Front Desk / Admin / Manager to register a new student."""

    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-input"}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-input"}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))

    class Meta:
        model = Student
        fields = [
            "date_of_birth",
            "college",
            "passed_year",
            "gpa",
            "test_type",
            "test_score",
            "preferred_country",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "college": forms.TextInput(attrs={"class": "form-input"}),
            "passed_year": forms.NumberInput(attrs={"class": "form-input"}),
            "gpa": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "test_type": forms.Select(attrs={"class": "form-input"}),
            "test_score": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "preferred_country": forms.TextInput(attrs={"class": "form-input"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True, branch=None):
        student = super().save(commit=False)
        user = User(
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name", ""),
            phone=self.cleaned_data.get("phone", ""),
            role=User.Role.STUDENT,
            branch=branch,
        )
        user.set_unusable_password()
        if commit:
            user.save()
            student.user = user
            student.save()
        return student


class StudentEditForm(forms.ModelForm):
    """Used by Front Desk / Admin / Manager to edit an existing student's
    profile and basic account details."""

    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-input"}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))

    class Meta:
        model = Student
        fields = [
            "date_of_birth",
            "college",
            "passed_year",
            "gpa",
            "test_type",
            "test_score",
            "preferred_country",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "college": forms.TextInput(attrs={"class": "form-input"}),
            "passed_year": forms.NumberInput(attrs={"class": "form-input"}),
            "gpa": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "test_type": forms.Select(attrs={"class": "form-input"}),
            "test_score": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "preferred_country": forms.TextInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["phone"].initial = self.instance.user.phone

    def save(self, commit=True):
        student = super().save(commit=False)
        if commit:
            student.save()
            user = student.user
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data.get("last_name", "")
            user.phone = self.cleaned_data.get("phone", "")
            user.save(update_fields=["first_name", "last_name", "phone"])
        return student
