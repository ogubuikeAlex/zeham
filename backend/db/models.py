from datetime import datetime, timezone
import uuid

from typing import Optional

from sqlalchemy import String, BigInteger, DateTime, Boolean, Integer, Text, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tx_hash: Mapped[str] = mapped_column(String(66), nullable=False, index=True)
    block_number: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    block_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    contract_address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_address: Mapped[str] = mapped_column(String(42), nullable=True)
    to_address: Mapped[str] = mapped_column(String(42), nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    log_index: Mapped[int] = mapped_column(Integer, nullable=False)
    nansen_status: Mapped[str] = mapped_column(String(16), default='PENDING', index=True)
    nansen_labels: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class WatchedContract(Base):
    __tablename__ = 'watched_contracts'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    address: Mapped[str] = mapped_column(String(42), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(128), nullable=True)
    abi_path: Mapped[str] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Alert(Base):
    __tablename__ = 'alerts'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    contract_address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    anomaly_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(8), nullable=False)         # RULE | AI
    source_event_ids: Mapped[list] = mapped_column(ARRAY(String), nullable=True, unique=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    on_chain_tx: Mapped[str] = mapped_column(String(66), nullable=True)    # ERC-8004 Mantle tx
    fired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    # Sprint 3 (ADR-003) broadcaster output-tracking (FR-11).
    notified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)


class DetectionLog(Base):
    __tablename__ = 'detection_logs'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    contract_address: Mapped[str] = mapped_column(String(42), nullable=True, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str] = mapped_column(Text, nullable=True)
    event_ids: Mapped[list] = mapped_column(ARRAY(String), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Subscription(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (
        UniqueConstraint('contract_address', 'telegram_chat_id',
                         name='uq_subscriptions_contract_chat'),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    contract_address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DeadLetter(Base):
    __tablename__ = 'dead_letters'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tx_hash: Mapped[str] = mapped_column(String(66), nullable=True)
    log_index: Mapped[int] = mapped_column(Integer, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
