from rest_framework import serializers
from apps.payments.models import Payment
from apps.payments.models import PaymentAttempt


class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text = "Payment amount",
    )

    currency = serializers.CharField(
        max_length=3,
        default="NRP",
        help_text = "Currency Code"
    )

    customer_email = serializers.EmailField(
        help_text = "Customer email address",
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text = "Payment Description",
    )

    idempotency_key = serializers.CharField(
        max_length=255,
        help_text ="Unique key to prevent duplicate payments"
    )

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment

        fields = [
            "id",
            "amount",
            "currency",
            "customer_email",
            "description",
            "status",
            "retry_count",
            "max_retries",
            "next_retry_at",
            "gateway_reference",
            "created_at",
        ]

        read_only_fields = fields    
        
class PaymentAttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAttempt

        fields = [
            "attempt_number",
            "status",
            "response_code",
            "response_message",
            "duration_ms",
            "created_at",
        ]        