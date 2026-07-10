from rest_framework import serializers
from apps.payments.models import Payment
from apps.payments.models import PaymentAttempt


class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = serializers.CharField(
        max_length=3,
        default="NRP",
    )

    customer_email = serializers.EmailField()

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    idempotency_key = serializers.CharField(
        max_length=255,
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