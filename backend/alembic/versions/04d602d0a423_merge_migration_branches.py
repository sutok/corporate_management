"""merge_migration_branches

Revision ID: 04d602d0a423
Revises: 4903fe892a89, 5d038c81c941
Create Date: 2026-01-03 11:35:54.843794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04d602d0a423'
down_revision: Union[str, None] = ('4903fe892a89', '5d038c81c941')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
