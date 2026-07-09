from datetime import timedelta

from django.utils import timezone

class RetryPolicy:
        def should_retry(self, payment, gateway_response):

            if not gateway_response.retryable:
                return False

            return payment.retry_count < payment.max_retries
        
        def next_retry_time(self, payment):
            
            delay_minutes = 2 ** payment.retry_count
            
            return timezone.now() + timedelta(
                minutes= delay_minutes
            )