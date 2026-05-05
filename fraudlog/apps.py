from django.apps import AppConfig
from .tasks import preload_fraud_rules_task, warmup_fraud_summary_task

class FraudlogConfig(AppConfig):
    name = 'fraudlog'

    def ready(self):
        preload_fraud_rules_task.delay()
        warmup_fraud_summary_task.delay()