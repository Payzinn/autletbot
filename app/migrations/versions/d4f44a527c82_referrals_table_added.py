"""referrals table added

Revision ID: d4f44a527c82
Revises: de143c91fee5
Create Date: 2025-08-20 15:13:29.623269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f44a527c82'
down_revision: Union[str, Sequence[str], None] = 'de143c91fee5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу referrals
    op.create_table(
        'referrals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('referral_link', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'DISABLED', name='referralstatus'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Конвертируем колонку referral_link в users в INTEGER
    op.execute(
        "ALTER TABLE users ALTER COLUMN referral_link TYPE INTEGER USING referral_link::integer"
    )

    # Добавляем недостающий столбец для FK
    op.add_column('users', sa.Column('referral_id', sa.Integer(), nullable=True))

    # Создаем внешний ключ
    op.create_foreign_key(
        "fk_users_referral_id",
        "users",
        "referrals",
        ["referral_id"],
        ["id"]
    )
    
def downgrade() -> None:
    op.drop_constraint("fk_users_referral_id", 'users', type_='foreignkey')
    op.alter_column(
        'users',
        'referral_id',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
    op.drop_table('referrals')