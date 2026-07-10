import django_filters

from apps.payments.models import Payment


class PaymentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="iexact",
    )

    customer_email = django_filters.CharFilter(
        field_name="customer_email",
        lookup_expr="icontains",
    )

    currency = django_filters.CharFilter(
        field_name="currency",
        lookup_expr="iexact",
    )

    min_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
    )

    max_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Payment
        fields = [
            
        ]