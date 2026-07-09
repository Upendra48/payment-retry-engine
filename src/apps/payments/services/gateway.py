import random
import time
from uuid import uuid4

from apps.common.gateway import GatewayOutcome
from .dto import GatewayResponse


class MockGatewayService:
    def process(self) -> GatewayResponse:
        start = time.perf_counter()

        outcome = random.choice(
            [
                GatewayOutcome.SUCCESS,
                GatewayOutcome.TIMEOUT,
                GatewayOutcome.SERVER_ERROR,
                GatewayOutcome.CARD_DECLINED,
            ]
        )

        duration = int((time.perf_counter() - start) * 1000)

        match outcome:

            case GatewayOutcome.SUCCESS:
                return GatewayResponse(
                    success=True,
                    retryable=False,
                    response_code="200",
                    response_message="Payment successful",
                    gateway_transaction_id=str(uuid4()),
                    duration_ms=duration,
                )

            case GatewayOutcome.TIMEOUT:
                return GatewayResponse(
                    success=False,
                    retryable=True,
                    response_code="TIMEOUT",
                    response_message="Gateway timeout",
                    duration_ms=duration,
                )

            case GatewayOutcome.SERVER_ERROR:
                return GatewayResponse(
                    success=False,
                    retryable=True,
                    response_code="503",
                    response_message="Gateway unavailable",
                    duration_ms=duration,
                )

            case GatewayOutcome.CARD_DECLINED:
                return GatewayResponse(
                    success=False,
                    retryable=False,
                    response_code="402",
                    response_message="Card declined",
                    duration_ms=duration,
                )