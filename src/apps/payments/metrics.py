from prometheus_client import Counter, Gauge, Histogram

payments_created_total = Counter(
    "payments_created_total",
    "Total number of payments created",
)

payments_success_total = Counter(
    "payments_success_total",
    "Total number of successful payments",
)

payments_failed_total = Counter(
    "payments_failed_total",
    "Total number of failed payments",
)

payment_retries_total = Counter(
    "payment_retries_total",
    "Total number of payment retries",
)

payments_retrying_current = Gauge(
    "payments_retrying_current",
    "Current number of payments waiting for retry",
)

gateway_latency_seconds = Histogram(
    "gateway_latency_seconds",
    "Time spent communicating with the payment gateway",
)

payment_processing_seconds = Histogram(
    "payment_processing_seconds",
    "Time spent processing a payment",
)