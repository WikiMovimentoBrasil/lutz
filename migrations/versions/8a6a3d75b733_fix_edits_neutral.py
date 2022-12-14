"""Fix edits_neutral

Revision ID: 8a6a3d75b733
Revises: 39b35b729b8a
Create Date: 2022-12-17 02:39:46.582660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8a6a3d75b733'
down_revision = '39b35b729b8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('snapshot', sa.Column('edits_neutral', sa.Integer(), nullable=True))
    op.drop_column('snapshot', 'edtis_neutral')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('snapshot', sa.Column('edtis_neutral', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('snapshot', 'edits_neutral')
    # ### end Alembic commands ###
