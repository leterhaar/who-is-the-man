"""added team column for user

Revision ID: a218ae4e41fd
Revises: 8e3bf7d19964
Create Date: 2020-07-01 10:13:18.370468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a218ae4e41fd'
down_revision = '8e3bf7d19964'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('team', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'team')
    # ### end Alembic commands ###
