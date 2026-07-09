from django.db import models

from apps.common.constants import AttemptStatus
from apps.common.models import TimeStampedUUIDModel

from .payment import Payment


class PaymentAttempt(TimeStampedUUIDModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    attempt_number = models.PositiveSmallIntegerField()
    
    is_retry = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=AttemptStatus.choices,
    )

    response_code = models.CharField(
        max_length=50,
    )

    response_message = models.TextField()

    duration_ms = models.PositiveIntegerField()

    gateway_transaction_id = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ["attempt_number"]
        constraints =[
            models.UniqueConstraint(
                fields=["payment", "attempt_number"],
                name = "unique_payment_attempt_number",
            )
        ]
        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.payment_id} - Attempt {self.attempt_number}"