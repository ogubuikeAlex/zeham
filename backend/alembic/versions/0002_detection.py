from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0002_detection'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'events',
        sa.Column('processed', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
    )
    op.create_index('idx_events_processed', 'events', ['processed', 'nansen_status'])

    # --- replace the placeholder alerts table with the ADR-002 final schema ---
    op.drop_index('idx_alerts_event_id', table_name='alerts')
    op.drop_table('alerts')
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('contract_address', sa.String(42), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('anomaly_type', sa.String(32), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('source', sa.String(8), nullable=False),               # RULE | AI
        sa.Column('source_event_ids', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('on_chain_tx', sa.String(66), nullable=True),
        sa.Column('fired_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('notified', sa.Boolean(), server_default=sa.text('FALSE')),
        sa.UniqueConstraint('source_event_ids', name='uq_alerts_source_event_ids'),
    )
    op.create_index('idx_alerts_severity', 'alerts', ['severity'])
    op.create_index('idx_alerts_contract', 'alerts', ['contract_address'])
    op.create_index('idx_alerts_fired_at', 'alerts', [sa.text('fired_at DESC')])
    op.create_index('idx_alerts_notified', 'alerts', ['notified'])

    op.create_table(
        'detection_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('contract_address', sa.String(42), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('event_ids', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('logged_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_detection_logs_contract', 'detection_logs', ['contract_address'])


def downgrade() -> None:
    op.drop_index('idx_detection_logs_contract', table_name='detection_logs')
    op.drop_table('detection_logs')

    op.drop_index('idx_alerts_notified', table_name='alerts')
    op.drop_index('idx_alerts_fired_at', table_name='alerts')
    op.drop_index('idx_alerts_contract', table_name='alerts')
    op.drop_index('idx_alerts_severity', table_name='alerts')
    op.drop_table('alerts')
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

    op.drop_index('idx_events_processed', table_name='events')
    op.drop_column('events', 'processed')
