"""minor changes to hike model

Revision ID: 889433a1c3fb
Revises: 1cc193cb0099
Create Date: 2023-01-26 15:17:52.121548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '889433a1c3fb'
down_revision = '1cc193cb0099'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hike', schema=None) as batch_op:
        batch_op.alter_column('distance',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.drop_index('ix_hike_timestamp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hike', schema=None) as batch_op:
        batch_op.create_index('ix_hike_timestamp', ['timestamp'], unique=False)
        batch_op.alter_column('distance',
               existing_type=sa.FLOAT(),
               nullable=True)

    # ### end Alembic commands ###
