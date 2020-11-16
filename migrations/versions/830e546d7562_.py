"""empty message

<<<<<<< HEAD:migrations/versions/830e546d7562_.py
Revision ID: 830e546d7562
Revises: 
Create Date: 2020-11-16 20:07:28.342714
=======
Revision ID: 7651b014bc1e
Revises: 
Create Date: 2020-11-15 22:21:30.884374
>>>>>>> 9b03861d2c8bf5d63284e272641bdeb205406c96:migrations/versions/7651b014bc1e_.py

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
<<<<<<< HEAD:migrations/versions/830e546d7562_.py
revision = '830e546d7562'
=======
revision = '7651b014bc1e'
>>>>>>> 9b03861d2c8bf5d63284e272641bdeb205406c96:migrations/versions/7651b014bc1e_.py
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image', sa.String(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('is_archived', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('image'),
    sa.UniqueConstraint('name')
    )
    op.create_table('guilds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('discord', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('role', sa.Enum('GUEST', 'VERIFIED', 'ADMIN', name='role'), nullable=False),
    sa.Column('theme', sa.Enum('DEFAULT', 'BLUE_RASPBERRY', 'SEABREEZE', 'CARTOGRAPHY', 'PUMPKIN_SPICE', 'RED', name='theme'), nullable=False),
    sa.Column('discord_confirmed', sa.Boolean(), nullable=False),
    sa.Column('guild_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('discord'),
    sa.UniqueConstraint('username')
    )
    op.create_table('worlds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image', sa.String(), nullable=False),
    sa.Column('center_lat', sa.Float(), nullable=False),
    sa.Column('center_lng', sa.Float(), nullable=False),
    sa.Column('radius', sa.Float(), nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('image')
    )
    op.create_table('pins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position_x', sa.Float(), nullable=False),
    sa.Column('position_y', sa.Float(), nullable=False),
    sa.Column('symbol', sa.Enum('STONE', 'STONE_MOTHERLODE', 'ORE', 'ORE_MOTHERLODE', 'WOOD', 'ANIMAL', 'ANIMAL_BOSS', 'MOB', 'MOB_BOSS', 'WELL', 'GRAVE', 'TACTICAL_HOUSE', 'TACTICAL_FIRE', 'TACTICAL_FISH', name='symbol'), nullable=False),
    sa.Column('resource', sa.Enum('YEW', 'BIRCH', 'ASH', 'OAK', 'SPRUCE', 'COPPER', 'TIN', 'IRON', 'SILVER', 'AURELIUM', 'GRANITE', 'LIMESTONE', 'TRAVERTINE', 'SLATE', 'MARBLE', 'SPIDER', 'PIG', 'CAT', 'AUROCH', 'ELK', 'WOLF', 'HUMAN', 'ELVEN', 'MONSTER', 'STONEBORN', 'GUINECIAN', 'NA', name='resource'), nullable=False),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('respawn', sa.Integer(), nullable=True),
    sa.Column('world_id', sa.Integer(), nullable=False),
    sa.Column('x_cord', sa.String(length=1), nullable=True),
    sa.Column('y_cord', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('edits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('details', sa.String(), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=False),
    sa.Column('pin_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pin_id'], ['pins.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('edits')
    op.drop_table('pins')
    op.drop_table('worlds')
    op.drop_table('users')
    op.drop_table('guilds')
    op.drop_table('campaigns')
    # ### end Alembic commands ###
