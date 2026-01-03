"""add_company_id_to_subscription_history

Revision ID: ded2fec7a1a2
Revises: b81e7a91fd55
Create Date: 2026-01-01 21:33:49.459153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ded2fec7a1a2'
down_revision: Union[str, None] = 'b81e7a91fd55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add company_id column as nullable first
    op.add_column('service_subscription_history',
        sa.Column('company_id', sa.Integer(), nullable=True, comment='企業ID')
    )

    # Populate company_id from company_service_subscriptions
    op.execute("""
        UPDATE service_subscription_history ssh
        SET company_id = css.company_id
        FROM company_service_subscriptions css
        WHERE ssh.subscription_id = css.id
    """)

    # Make company_id NOT NULL
    op.alter_column('service_subscription_history', 'company_id',
        existing_type=sa.Integer(),
        nullable=False
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_service_subscription_history_company_id',
        'service_subscription_history', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )

    # Add index
    op.create_index(
        'ix_service_subscription_history_company_id',
        'service_subscription_history',
        ['company_id']
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_service_subscription_history_company_id', table_name='service_subscription_history')

    # Remove foreign key
    op.drop_constraint('fk_service_subscription_history_company_id', 'service_subscription_history', type_='foreignkey')

    # Remove column
    op.drop_column('service_subscription_history', 'company_id')
