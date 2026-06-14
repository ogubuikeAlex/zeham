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


settings = Settings()
