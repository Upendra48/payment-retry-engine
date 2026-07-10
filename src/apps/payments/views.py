from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.serializers import (
    PaymentAttemptSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
)

from apps.payments.services.dto import CreatePaymentRequest
from apps.payments.services.payment_service import PaymentService

from rest_framework.permissions import AllowAny

from rest_framework import generics
from apps.payments.models import Payment

from apps.payments.models import PaymentAttempt


class PaymentCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
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
        
        
class PaymentDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single payment.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]     
    
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