from decimal import Decimal
from django.db import models

from apps.common.constants import PaymentStatus
from apps.common.models import TimeStampedUUIDModel

class Payment(TimeStampedUUIDModel):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    
    currency = models.CharField(
        max_length=3,
        default='NRP',
    )
    
    customer_email = models.EmailField()
    
    status = models.CharField(
        max_length=20,
        choices= PaymentStatus.choices,
        default= PaymentStatus.PENDING,
        db_index= True,
    )
    
    retry_count = models.PositiveSmallIntegerField(default=0)
    
    max_retries = models.PositiveSmallIntegerField(default=3)
    
    next_retry_at = models.DateTimeField(
        null= True,
        blank= True,
    )
    
    gateway_reference = models.CharField(
        max_length= 100,
        blank= True,
    )
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["next_retry_at"]),
        ]
        
    def __str__(self):
        return f"{self.id} - {self.status}"    