"""added hike/user rel

Revision ID: 92367a6200ab
Revises: aea2cb047cd8
Create Date: 2023-01-21 14:54:08.886719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92367a6200ab'
down_revision = 'aea2cb047cd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hike', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('user-hike-key', 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hike', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
