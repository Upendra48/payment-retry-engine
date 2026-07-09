from celery import shared_task

from apps.payments.models import Payment
from apps.payments.services.payment_service import PaymentService


@shared_task(bind=True, max_retries=0)
def retry_payment_task(self, payment_id):
    """
    Retry an existing payment.
    """

    payment = Payment.objects.get(id=payment_id)

    service = PaymentService()

    service.retry_payment(payment)