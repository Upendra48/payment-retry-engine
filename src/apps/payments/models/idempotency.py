from django.db import models

from apps.common.models import TimeStampedUUIDModel

from .payment import Payment


class IdempotencyKey(TimeStampedUUIDModel):
    key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="idempotency_key",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.key