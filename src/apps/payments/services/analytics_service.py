from django.db.models import Avg, Count, Q, Sum

from apps.common.constants import PaymentStatus
from apps.payments.models import Payment


class AnalyticsService:

    def get_summary(self):
        queryset = Payment.objects.all()

        summary = queryset.aggregate(
            total_payments=Count("id"),

            successful_payments=Count(
                "id",
                filter=Q(status=PaymentStatus.SUCCESS),
            ),

            failed_payments=Count(
                "id",
                filter=Q(status=PaymentStatus.FAILED),
            ),

            retrying_payments=Count(
                "id",
                filter=Q(status=PaymentStatus.RETRYING),
            ),

            pending_payments=Count(
                "id",
                filter=Q(status=PaymentStatus.PENDING),
            ),

            total_amount_processed=Sum("amount"),

            successful_amount=Sum(
                "amount",
                filter=Q(status=PaymentStatus.SUCCESS),
            ),

            failed_amount=Sum(
                "amount",
                filter=Q(status=PaymentStatus.FAILED),
            ),

            average_retry_count=Avg("retry_count"),
        )

        total = summary["total_payments"] or 0
        success = summary["successful_payments"] or 0

        summary["success_rate"] = (
            round((success / total) * 100, 2)
            if total
            else 0
        )

        summary["average_retry_count"] = round(
            summary["average_retry_count"] or 0,
            2,
        )

        return summary