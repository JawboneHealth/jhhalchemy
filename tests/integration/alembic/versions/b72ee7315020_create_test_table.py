"""create test table

Revision ID: b72ee7315020
Revises: 
Create Date: 2018-01-15 19:56:13.922149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b72ee7315020'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'DropThis',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('time_removed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('time_created', sa.Integer(), server_default=sa.text(u'unix_timestamp()'), nullable=False),
        sa.Column(
            'time_modified',
            sa.TIMESTAMP(),
            server_default=sa.text(u'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
            nullable=False),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('DropThis')
