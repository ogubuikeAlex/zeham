import json
import logging

from web3 import AsyncWeb3

from config import settings

logger = logging.getLogger(__name__)

DEFAULT_ERC8004_ABI = [{
    'inputs': [
        {'internalType': 'string', 'name': '_anomalyType', 'type': 'string'},
        {'internalType': 'string', 'name': '_severity', 'type': 'string'},
        {'internalType': 'string', 'name': '_reason', 'type': 'string'},
        {'internalType': 'string', 'name': '_contractTarget', 'type': 'string'},
        {'internalType': 'bool', 'name': '_isAnomaly', 'type': 'bool'},
    ],
    'name': 'logDecision',
    'outputs': [],
    'stateMutability': 'nonpayable',
    'type': 'function',
}]


def _load_abi() -> list:
    if settings.erc8004_abi_path:
        try:
            with open(settings.erc8004_abi_path, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception as e:
            logger.warning('could not load ERC-8004 ABI file; using default',
                           extra={'path': settings.erc8004_abi_path, 'error': str(e)})
    return DEFAULT_ERC8004_ABI


class ChainLogger:

    def __init__(self):
        self.abi = _load_abi()

    @property
    def enabled(self) -> bool:
        return bool(settings.agent_private_key and settings.erc8004_contract_address)

    async def log_decision(self, anomaly_type: str, severity: str, reason: str,
                           contract_target: str = '', is_anomaly: bool = True) -> str | None:
        if not self.enabled:
            logger.info('chain logging disabled (no key/contract); on_chain_tx will be NULL')
            return None
        try:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.mantle_http_url))
            account = w3.eth.account.from_key(settings.agent_private_key)
            contract = w3.eth.contract(
                address=w3.to_checksum_address(settings.erc8004_contract_address),
                abi=self.abi,
            )
            nonce = await w3.eth.get_transaction_count(account.address)
            gas_price = await w3.eth.gas_price
            chain_id = await w3.eth.chain_id
            tx = await contract.functions.logDecision(
                anomaly_type, severity, reason[:200],   # cap reason for gas
                contract_target, is_anomaly,
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': settings.erc8004_gas_limit,
                'gasPrice': gas_price,
                'chainId': chain_id,
            })
            signed = account.sign_transaction(tx)
            raw = getattr(signed, 'raw_transaction', None) or signed.rawTransaction
            tx_hash = await w3.eth.send_raw_transaction(raw)
            tx_hex = tx_hash.hex()
            logger.info('on-chain decision logged', extra={'tx_hash': tx_hex})
            return tx_hex
        except Exception as e:
            logger.error('chain write failed', extra={'error': str(e)})
            return None
