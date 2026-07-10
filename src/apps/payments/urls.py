from django.urls import path

from apps.payments.views import PaymentCreateAPIView
from apps.payments.views import (
    PaymentAttemptListAPIView,
    PaymentCreateAPIView,
    PaymentDetailAPIView,
)

urlpatterns = [
    path(
        "",
        PaymentCreateAPIView.as_view(),
        name="payment-create",
    ),
    
    path(
        "<uuid:pk>/",
        PaymentDetailAPIView.as_view(),
        name = "payment-detail",
    ),
    
    path(
        "<uuid:payment_id>/attempts/",
        PaymentAttemptListAPIView.as_view(),
        name = "payment-attempts",
    ),
]