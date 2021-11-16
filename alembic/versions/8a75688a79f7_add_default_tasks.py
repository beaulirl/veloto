"""Add default tasks

Revision ID: 8a75688a79f7
Revises: 9418622ec720
Create Date: 2021-11-16 16:34:10.113111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a75688a79f7'
down_revision = '9418622ec720'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO task (id, name, every)
        VALUES (1, 'Смазать цепь', 10000),
               (2, 'Проверить колодки', 12500),
               (3, 'Заменить ролики заднего переключателя', 300000);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM task WHERE id IN (1, 2, 3);
        """
    )
