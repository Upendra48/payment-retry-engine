from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    RETRYING = "RETRYING", "Retrying"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"


class AttemptStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"