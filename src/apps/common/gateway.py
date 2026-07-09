from enum import Enum


class GatewayOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    SERVER_ERROR = "SERVER_ERROR"
    CARD_DECLINED = "CARD_DECLINED"