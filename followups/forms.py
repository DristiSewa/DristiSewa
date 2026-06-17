from django import forms

from .models import Appointment, FollowUp


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ["student", "assigned_to", "note", "scheduled_date", "is_done"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-input"}),
            "assigned_to": forms.Select(attrs={"class": "form-input"}),
            "note": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "scheduled_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "is_done": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["student", "staff", "purpose", "appointment_date", "appointment_time", "status", "notes"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-input"}),
            "staff": forms.Select(attrs={"class": "form-input"}),
            "purpose": forms.TextInput(attrs={"class": "form-input"}),
            "appointment_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
