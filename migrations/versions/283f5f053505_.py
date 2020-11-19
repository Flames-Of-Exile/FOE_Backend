"""empty message

Revision ID: 283f5f053505
Revises: 341063e49c43
Create Date: 2020-11-19 18:47:59.230119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '283f5f053505'
down_revision = '341063e49c43'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE resource ADD VALUE 'BEAR'")
    op.execute("ALTER TYPE resource ADD VALUE 'GRYPHON'")


def downgrade():
    pass
