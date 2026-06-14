from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tx_hash', sa.String(66), nullable=False),
        sa.Column('block_number', sa.BigInteger(), nullable=False),
        sa.Column('block_timestamp', sa.DateTime(timezone=True)),
        sa.Column('contract_address', sa.String(42), nullable=False),
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('from_address', sa.String(42), nullable=True),
        sa.Column('to_address', sa.String(42), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=False),
        sa.Column('log_index', sa.Integer(), nullable=False),
        sa.Column('nansen_status', sa.String(16), server_default='PENDING'),
        sa.Column('nansen_labels', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('tx_hash', 'log_index', name='uq_events_tx_log'),
    )
    op.create_index('idx_events_contract', 'events', ['contract_address'])
    op.create_index('idx_events_block', 'events', ['block_number'])
    op.create_index('idx_events_event_type', 'events', ['event_type'])
    op.create_index('idx_events_nansen_stat', 'events', ['nansen_status'])
    op.create_index('idx_events_created_at', 'events', [sa.text('created_at DESC')])

    op.create_table(
        'watched_contracts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('address', sa.String(42), nullable=False, unique=True),
        sa.Column('label', sa.String(128), nullable=True),
        sa.Column('abi_path', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('TRUE')),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_table(
        'alerts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('severity', sa.String(16), nullable=True),
        sa.Column('category', sa.String(64), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_alerts_event_id', 'alerts', ['event_id'])

    op.create_table(
        'dead_letters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tx_hash', sa.String(66), nullable=True),
        sa.Column('log_index', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )


def downgrade() -> None:
    op.drop_table('dead_letters')
    op.drop_index('idx_alerts_event_id', table_name='alerts')
    op.drop_table('alerts')
    op.drop_table('watched_contracts')
    op.drop_index('idx_events_created_at', table_name='events')
    op.drop_index('idx_events_nansen_stat', table_name='events')
    op.drop_index('idx_events_event_type', table_name='events')
    op.drop_index('idx_events_block', table_name='events')
    op.drop_index('idx_events_contract', table_name='events')
    op.drop_table('events')
