from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6b464df52dcc'
down_revision: Union[str, Sequence[str], None] = '574eb2eb5fe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Создаём Enum тип отдельно
user_status_enum = sa.Enum('ADMIN', 'USER', name='user_status')

def upgrade() -> None:
    # 1. Создаём новый enum-тип
    user_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Добавляем колонку
    op.add_column('users',
        sa.Column('status', user_status_enum, nullable=False, server_default='USER')
    )


def downgrade() -> None:
    # 1. Удаляем колонку
    op.drop_column('users', 'status')

    # 2. Удаляем enum-тип
    user_status_enum.drop(op.get_bind(), checkfirst=True)
