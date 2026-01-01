"""add_company_id_to_daily_reports

Revision ID: 4903fe892a89
Revises: ded2fec7a1a2
Create Date: 2026-01-01 21:44:55.353520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4903fe892a89'
down_revision: Union[str, None] = 'ded2fec7a1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add company_id column as nullable first
    op.add_column('daily_reports',
        sa.Column('company_id', sa.Integer(), nullable=True, comment='企業ID')
    )

    # Populate company_id from users
    op.execute("""
        UPDATE daily_reports dr
        SET company_id = u.company_id
        FROM users u
        WHERE dr.user_id = u.id
    """)

    # Make company_id NOT NULL
    op.alter_column('daily_reports', 'company_id',
        existing_type=sa.Integer(),
        nullable=False
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_daily_reports_company_id',
        'daily_reports', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )

    # Add index
    op.create_index(
        'ix_daily_reports_company_id',
        'daily_reports',
        ['company_id']
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_daily_reports_company_id', table_name='daily_reports')

    # Remove foreign key
    op.drop_constraint('fk_daily_reports_company_id', 'daily_reports', type_='foreignkey')

    # Remove column
    op.drop_column('daily_reports', 'company_id')
