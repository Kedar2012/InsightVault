# fraud/tasks.py
from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@shared_task(name="preload_fraud_rules_task")
def preload_fraud_rules_task():
    """Preload fraud detection thresholds into Redis cache."""
    fraud_thresholds = {
        "reversal_limit": 5,
        "high_amount_limit": 100000,
    }
    cache.set("fraud_thresholds", fraud_thresholds, timeout=None)
    logger.info("Fraud thresholds cached successfully.")

@shared_task(name="warmup_fraud_summary_task")
def warmup_fraud_summary_task():
    """Warm up fraud summary in cache."""
    summary = {"total_flags": 0, "high": 0, "medium": 0, "low": 0}
    cache.set("fraud_summary", summary, timeout=300)
    logger.info("Fraud summary cached successfully.")
