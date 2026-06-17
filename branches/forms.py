from django import forms

from .models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["name", "code", "address", "phone", "email", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "code": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class StaffAssignForm(forms.Form):
    """Used on the branch_staff page to assign an existing staff user to a branch."""

    user_id = forms.IntegerField(widget=forms.HiddenInput)
    branch_id = forms.IntegerField(widget=forms.HiddenInput)
