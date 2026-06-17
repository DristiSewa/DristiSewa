from django import forms

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_type", "file"]
        widgets = {
            "doc_type": forms.Select(attrs={"class": "form-input"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-input"}),
        }


class DocumentReviewForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["status", "remarks"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-input"}),
            "remarks": forms.TextInput(attrs={"class": "form-input"}),
        }
