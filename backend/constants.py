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


