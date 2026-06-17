from django import forms

from applications.models import Application


class ApplicationStatusUpdateForm(forms.ModelForm):
    """Used by Front Desk to update a student's application/pipeline status.

    Reuses the existing `Application.Status` choices (the only
    database-backed status field already present in the Student-related
    schema) rather than introducing a new status field/model.
    """

    class Meta:
        model = Application
        fields = ["status", "remarks"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
