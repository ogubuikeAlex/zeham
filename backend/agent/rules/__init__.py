from .base import BaseRule, RuleAlert
from .flash_loan import FlashLoanRule
from .rug_pull import RugPullRule
from .whale import WhaleMoveRule
from .wash_trade import WashTradeRule
from .exploit import ContractExploitRule

ALL_RULES = [
    FlashLoanRule(),
    RugPullRule(),
    WhaleMoveRule(),
    WashTradeRule(),
    ContractExploitRule(),
]

__all__ = [
    'BaseRule', 'RuleAlert', 'ALL_RULES',
    'FlashLoanRule', 'RugPullRule', 'WhaleMoveRule', 'WashTradeRule',
    'ContractExploitRule',
]
