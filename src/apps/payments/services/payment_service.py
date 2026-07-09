from django.db import transaction
from apps.payments.services.gateway import MockGatewayService

from apps.payments.models import IdempotencyKey, Payment

from apps.common.constants import AttemptStatus
from apps.payments.models import PaymentAttempt

from apps.common.constants import PaymentStatus


class PaymentService:
    
    def __init__(self, gateway = None):
        self.gateway = gateway or MockGatewayService()
        
    @transaction.atomic
    def create_payment(self, request):
        payment = self._find_existing_payment(request.idempotency_key)

        if payment:
            return payment

        payment = self._create_payment(request)

        self._create_idempotency_record(
            request.idempotency_key,
            payment,
        )
        
        gateway_response = self.gateway.process()
        
        self._record_attempt(payment, gateway_response,)
        
        self._update_payment_status(
            payment, gateway_response,
        )

        return payment
    
    def _record_attempt(self, payment, response):
        PaymentAttempt.objects.create(
        payment=payment,
        attempt_number=1,
        status=(
            AttemptStatus.SUCCESS
            if response.success
            else AttemptStatus.FAILED
        ),
        response_code=response.response_code,
        response_message=response.response_message,
        duration_ms=response.duration_ms,
        gateway_transaction_id=response.gateway_transaction_id or "",
    )
        
    def _update_payment_status(self, payment, response):
       if response.success:
        payment.status = PaymentStatus.SUCCESS
        payment.gateway_reference = response.gateway_transaction_id

       elif response.retryable:
        payment.status = PaymentStatus.RETRYING

       else:
        payment.status = PaymentStatus.FAILED

       payment.save(
        update_fields=[
            "status",
            "gateway_reference",
            "updated_at",
        ]
    )    
    
    
    def _find_existing_payment(self, key):
        record = (
        IdempotencyKey.objects
        .select_related("payment")
        .filter(key=key)
        .first()
        )

        if record:
            return record.payment

        return None
    
    def _create_payment(self, request):
        return Payment.objects.create(
            amount = request.amount,
            currency = request.currency,
            customer_email = request.customer_email,
            description = request.description,
        )
        
    def _create_idempotency_record(self,key,payment):
        return IdempotencyKey.objects.create(
            key=key,
            payment=payment,
        )    