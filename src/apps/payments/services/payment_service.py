from django.db import transaction
from apps.payments.services.gateway import MockGatewayService

from apps.payments.models import IdempotencyKey, Payment

from apps.common.constants import AttemptStatus
from apps.payments.models import PaymentAttempt

from apps.common.constants import PaymentStatus

from apps.payments.services.retry_policy import RetryPolicy

from apps.payments.metrics import payments_created_total

from apps.payments.metrics import (
    payments_success_total,
    payments_failed_total,
)

from apps.payments.metrics import payment_retries_total

from apps.payments.metrics import gateway_latency_seconds

from apps.payments.metrics import payment_processing_seconds



class PaymentService:
    
    def __init__(self, gateway = None, retry_policy= None):
        self.gateway = gateway or MockGatewayService()
        self.retry_policy = retry_policy or RetryPolicy()
        
    @transaction.atomic
    def create_payment(self, request):
        
        with payment_processing_seconds.time():
            
          payment = self._find_existing_payment(request.idempotency_key)

          if payment:
            return payment

          payment = self._create_payment(request)

          self._create_idempotency_record(
            request.idempotency_key,
            payment,
          )
        
          self._process_gateway(payment)

          return payment
    
    def _record_attempt(self, payment, response):
        PaymentAttempt.objects.create(
        payment=payment,
        attempt_number=payment.attempts.count() + 1,
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
        
        payments_success_total.inc()

       elif self.retry_policy.should_retry(payment, response):
           payment.status = PaymentStatus.RETRYING
        
           payment.retry_count += 1
        
           payment.next_retry_at = (
            self.retry_policy.next_retry_time(payment)
            )
           
           payment_retries_total.inc()
        
    
       else:
           payment.status = PaymentStatus.FAILED
           
           payments_failed_total.inc()

       payment.save(
        update_fields=[
            "status",
            "retry_count",
            "next_retry_at",
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
        payment = Payment.objects.create(
            amount = request.amount,
            currency = request.currency,
            customer_email = request.customer_email,
            description = request.description,
        )
        
        payments_created_total.inc()
        return payment
        
    def _create_idempotency_record(self,key,payment):
        return IdempotencyKey.objects.create(
            key=key,
            payment=payment,
        )    
        
    def _process_gateway(self, payment):

        gateway_response = self.gateway.process()

        self._record_attempt(
          payment,
          gateway_response,
         )

        self._update_payment_status(
          payment,
          gateway_response,
        )
        
        gateway_latency_seconds.observe(
            gateway_response.duration_ms / 1000
        )

        return gateway_response    
    
    
    def retry_payment(self, payment):
        
        if payment.status not in [PaymentStatus.RETRYING, PaymentStatus.PENDING]:
            return payment
        
        self._process_gateway(payment)
        
        return payment