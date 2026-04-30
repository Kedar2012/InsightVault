from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "transaction_type", "description"]
        widgets = {
            "transaction_type": forms.Select(choices=Transaction._meta.get_field("transaction_type").choices),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
