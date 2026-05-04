from django import template
from transactions.models import DebitTransaction, CreditTransaction, ManualDebitTransaction

register = template.Library()

@register.filter
def get_type(tx):
    if isinstance(tx, DebitTransaction):
        return "debit"
    elif isinstance(tx, CreditTransaction):
        return "credit"
    elif isinstance(tx, ManualDebitTransaction):
        return "manual"
    return "unknown"
