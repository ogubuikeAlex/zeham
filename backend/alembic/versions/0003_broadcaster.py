from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0003_broadcaster'
down_revision: Union[str, None] = '0002_detection'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('idx_alerts_notified_at', 'alerts', [sa.text('notified_at DESC')])

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('contract_address', sa.String(42), nullable=False),
        sa.Column('telegram_chat_id', sa.String(32), nullable=True),
        sa.Column('label', sa.String(128), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('TRUE')),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('contract_address', 'telegram_chat_id',
                            name='uq_subscriptions_contract_chat'),
    )
    op.create_index('idx_subscriptions_contract', 'subscriptions', ['contract_address'])
    op.create_index('idx_subscriptions_chat', 'subscriptions', ['telegram_chat_id'])


def downgrade() -> None:
    op.drop_index('idx_subscriptions_chat', table_name='subscriptions')
    op.drop_index('idx_subscriptions_contract', table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_index('idx_alerts_notified_at', table_name='alerts')
    op.drop_column('alerts', 'notified_at')
