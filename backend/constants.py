from enum import Enum


class NansenStatus(str, Enum):
    PENDING = 'PENDING'
    DONE = 'DONE'
    UNAVAILABLE = 'UNAVAILABLE'


class EventType(str, Enum):
    TRANSFER = 'Transfer'
    SWAP = 'Swap'
    MINT = 'Mint'
    BURN = 'Burn'
    LIQUIDATION = 'Liquidation'
    APPROVAL = 'Approval'
    UNKNOWN = 'Unknown'


class MantleNetwork(str, Enum):
    TESTNET = 'testnet'
    MAINNET = 'mainnet'


class Severity(str, Enum):
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    NONE = 'NONE'


class AnomalyType(str, Enum):
    FLASH_LOAN = 'flash_loan'
    RUG_PULL = 'rug_pull'
    WHALE = 'whale'
    WASH_TRADE = 'wash_trade'
    EXPLOIT = 'exploit'
    SUSPICIOUS_PATTERN = 'suspicious_pattern'
    NONE = 'none'


class AlertSource(str, Enum):
    RULE = 'RULE'
    AI = 'AI'
