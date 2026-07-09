from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class CreatePaymentRequest:
    amount: Decimal
    currency: str
    customer_email: str
    description: str
    idempotency_key: str


@dataclass(slots=True)
class GatewayResponse:
    success: bool
    retryable: bool
    response_code: str
    response_message: str
    gateway_transaction_id: str | None = None
    duration_ms: int = 0