from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import MantleNetwork


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    mantle_network: MantleNetwork = MantleNetwork.TESTNET
    mantle_ws_url: str
    mantle_http_url: str

    database_url: str

    nansen_api_key: str
    nansen_base_url: str = 'https://api.nansen.ai/v1'

    log_level: str = 'INFO'
    log_json: bool = True

    # If set, callers must send this as a bearer token or X-API-Key header.
    watch_api_key: str | None = None

    enrich_interval_seconds: int = 30
    enrich_batch_size: int = 50
    nansen_cache_ttl_seconds: int = 300

    max_concurrent_handlers: int = 20
    backfill_on_reconnect: bool = True
    reconnect_max_retries: int = 5
    reconnect_base_delay: float = 2.0
    reconnect_max_delay: float = 60.0

    detection_enabled: bool = True
    detection_interval_seconds: int = 60       
    detection_max_events_per_batch: int = 50  

    ai_timeout_seconds: float = 15.0          
    elfa_api_key: str | None = None
    elfa_base_url: str = 'https://api.elfa.ai/v1'
    elfa_model: str = 'elfa-security-v1'
    altllm_api_key: str | None = None
    altllm_base_url: str = 'https://api.altllm.com/v1'
    altllm_model: str = 'altclaw-v1'

    agent_private_key: str | None = None
    erc8004_contract_address: str | None = None
    erc8004_abi_path: str | None = None        
    erc8004_gas_limit: int = 200_000
    erc8004_network: str = 'testnet'           

    broadcaster_enabled: bool = True
    broadcaster_interval_seconds: int = 10     
    broadcaster_batch_size: int = 50           
    dedup_window_minutes: int = 10             
    digest_interval_minutes: int = 10          

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_commands_enabled: bool = True     

    discord_webhook_url: str | None = None

    mantle_explorer_base: str = 'https://explorer.sepolia.mantle.xyz'
    mantle_explorer_api_key: str | None = None  

    self_api_base: str = 'http://localhost:8000'


settings = Settings()
