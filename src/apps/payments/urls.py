from django.urls import path

from apps.payments.views import (
    PaymentAttemptListAPIView,
    PaymentListCreateAPIView,
    PaymentDetailAPIView,
)

urlpatterns = [
    path(
        "",
        PaymentListCreateAPIView.as_view(),
        name="payment-list-create",
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