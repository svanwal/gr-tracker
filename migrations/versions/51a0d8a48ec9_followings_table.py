"""followings table

Revision ID: 51a0d8a48ec9
Revises: ee7a7afa4bff
Create Date: 2023-02-06 17:27:20.820074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51a0d8a48ec9'
down_revision = 'ee7a7afa4bff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('following',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['target_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('following')
    # ### end Alembic commands ###