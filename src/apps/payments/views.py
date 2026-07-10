from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.serializers import (
    PaymentAttemptSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
)

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

from apps.payments.services.dto import CreatePaymentRequest
from apps.payments.services.payment_service import PaymentService

from rest_framework.permissions import AllowAny

from rest_framework import generics
from apps.payments.models import Payment

from apps.payments.models import PaymentAttempt


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    permission_classes = [AllowAny]
    
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PaymentCreateSerializer
        return PaymentSerializer
    
    @extend_schema(
    summary="Create Payment",
    description="""
    Create a new payment.

    If the same idempotency key is sent multiple times,
    the existing payment is returned instead of creating
    a duplicate payment.
     """,
    request=PaymentCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=PaymentSerializer,
            description="Payment created successfully",
        ),
    },
    examples=[
        OpenApiExample(
            "Sample Request",
            value={
                "amount": "1000.00",
                "currency": "NRP",
                "customer_email": "user@example.com",
                "description": "Course Purchase",
                "idempotency_key": "payment-001",
            },
            request_only=True,
        ),
    ],
    )


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_request = CreatePaymentRequest(
            **serializer.validated_data,
        )

        payment = PaymentService().create_payment(
            payment_request,
        )

        response = PaymentSerializer(payment)

        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
        )
        
@extend_schema(
    summary="Retrieve Payment",
    description="Retrieve a payment by its UUID.",
)        
class PaymentDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single payment.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]    
    
 
     
    
@extend_schema(
    summary="Payment Attempts",
    description="Returns all gateway attempts for a payment.",
)    
class PaymentAttemptListAPIView(generics.ListAPIView):
    """
    List all attempts for a payment.
    """

    serializer_class = PaymentAttemptSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            PaymentAttempt.objects
            .filter(payment_id=self.kwargs["payment_id"])
            .order_by("attempt_number")
        )       
        
 