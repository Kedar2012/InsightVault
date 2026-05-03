from django import forms
from .models import FraudFlag

class FraudResolveForm(forms.ModelForm):
    class Meta:
        model = FraudFlag
        fields = ["resolved", "resolved_reason"]
        widgets = {
            "resolved_reason": forms.Textarea(attrs={"rows": 3, "placeholder": "Enter reason for marking as non-fraud"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("resolved") and not cleaned_data.get("resolved_reason"):
            raise forms.ValidationError("You must provide a reason when resolving a fraud flag.")
        return cleaned_data
