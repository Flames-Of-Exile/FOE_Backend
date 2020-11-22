"""empty message

Revision ID: 3ae558098c29
Revises: 283f5f053505
Create Date: 2020-11-21 16:38:09.851671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ae558098c29'
down_revision = '283f5f053505'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE resource ADD VALUE 'URGU'")
    op.execute("ALTER TYPE resource ADD VALUE 'ELEMENTALS'")
    op.execute("ALTER TYPE resource ADD VALUE 'SATYR'")
    op.execute("ALTER TYPE resource ADD VALUE 'ARACOIX'")
    op.execute("ALTER TYPE resource ADD VALUE 'UNDERHILL'")
    op.execute("ALTER TYPE resource ADD VALUE 'ENBARRI'")
    op.execute("ALTER TYPE resource ADD VALUE 'THRALLS'")


def downgrade():
    pass
