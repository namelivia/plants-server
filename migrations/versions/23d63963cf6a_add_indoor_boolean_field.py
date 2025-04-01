"""add_indoor_boolean_field

Revision ID: 23d63963cf6a
Revises: 8bfcf28920ea
Create Date: 2025-04-01 21:53:41.012639

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "23d63963cf6a"
down_revision = "8bfcf28920ea"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("plants", schema=None) as batch_op:
        batch_op.add_column(sa.Column("indoor", sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("plants", schema=None) as batch_op:
        batch_op.drop_column("indoor")

    # ### end Alembic commands ###
