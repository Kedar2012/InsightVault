from django import forms
from .models import DebitTransaction, CreditRequest

class DebitTransactionForm(forms.ModelForm):
    class Meta:
        model = DebitTransaction
        fields = ["amount", "destination_account_number", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "destination_account_number": forms.TextInput(attrs={"placeholder": "Enter destination account number"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dest_acc_no = cleaned_data.get("destination_account_number")
        if not dest_acc_no:
            raise forms.ValidationError("Destination account number is required for debit transactions.")
        return cleaned_data

class CreditRequestForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ["amount", "deposit_reference"]
        widgets = {
            "deposit_reference": forms.TextInput(attrs={"placeholder": "Enter cheque/receipt number"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("deposit_reference"):
            raise forms.ValidationError("Deposit reference is required for credit requests.")
        return cleaned_data

