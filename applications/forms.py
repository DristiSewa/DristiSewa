from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["destination_country", "institution", "status", "remarks"]
        widgets = {
            "destination_country": forms.TextInput(attrs={"class": "form-input"}),
            "institution": forms.TextInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class ApplicationStudentForm(forms.ModelForm):
    """Used by students on the Status Tracker page to submit a new
    application. Status is intentionally excluded - it always starts as
    "New" and can only be changed by staff."""

    class Meta:
        model = Application
        fields = ["destination_country", "institution", "remarks"]
        widgets = {
            "destination_country": forms.TextInput(attrs={"class": "form-input"}),
            "institution": forms.TextInput(attrs={"class": "form-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class ApplicationCreateForm(forms.ModelForm):
    """Used by Front Desk / Admin / Manager to start a new application on
    behalf of a student."""

    class Meta:
        model = Application
        fields = ["student", "destination_country", "institution", "status", "remarks"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-input"}),
            "destination_country": forms.TextInput(attrs={"class": "form-input"}),
            "institution": forms.TextInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
