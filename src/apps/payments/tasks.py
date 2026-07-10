from celery import shared_task
from django.utils import timezone

from apps.payments.models import Payment
from apps.payments.services.payment_service import PaymentService
from apps.common.constants import PaymentStatus


@shared_task(bind=True, max_retries=0)
def retry_payment_task(self, payment_id):
    payment = Payment.objects.get(id=payment_id)

    service = PaymentService()
    service.retry_payment(payment)


@shared_task
def retry_due_payments():
    payment_ids = (
        Payment.objects.filter(
            status=PaymentStatus.RETRYING,
            next_retry_at__lte=timezone.now(),
        )
        .values_list("id", flat=True)
    )

    count = 0

    for payment_id in payment_ids:
        retry_payment_task.delay(str(payment_id))
        count += 1

    return count