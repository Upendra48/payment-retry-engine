from django.db.models import Avg, Count, Q, Sum

from apps.common.constants import PaymentStatus
from apps.payments.models import Payment


class AnalyticsService:

    def get_summary(self):

        queryset = Payment.objects.all()

        total = queryset.count()

        successful = queryset.filter(
            status=PaymentStatus.SUCCESS
        ).count()

        failed = queryset.filter(
            status=PaymentStatus.FAILED
        ).count()

        retrying = queryset.filter(
            status=PaymentStatus.RETRYING
        ).count()

        pending = queryset.filter(
            status=PaymentStatus.PENDING
        ).count()

        success_rate = (
            round(successful / total * 100, 2)
            if total
            else 0
        )

        aggregates = queryset.aggregate(
            total_amount=Sum("amount"),

            successful_amount=Sum(
                "amount",
                filter=Q(status=PaymentStatus.SUCCESS),
            ),

            failed_amount=Sum(
                "amount",
                filter=Q(status=PaymentStatus.FAILED),
            ),

            average_retry=Avg("retry_count"),
        )

        return {
            "total_payments": total,
            "successful_payments": successful,
            "failed_payments": failed,
            "retrying_payments": retrying,
            "pending_payments": pending,
            "success_rate": success_rate,
            "total_amount_processed": aggregates["total_amount"] or 0,
            "successful_amount": aggregates["successful_amount"] or 0,
            "failed_amount": aggregates["failed_amount"] or 0,
            "average_retry_count": round(
                aggregates["average_retry"] or 0,
                2,
            ),
        }