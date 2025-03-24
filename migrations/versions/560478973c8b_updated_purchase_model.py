"""Updated purchase model

Revision ID: 560478973c8b
Revises: 6d4f294e105d
Create Date: 2025-03-24 10:10:07.565903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '560478973c8b'
down_revision = '6d4f294e105d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_address', sa.Text(), nullable=False))

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_provider', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('reference_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('payment_details', sa.JSON(), nullable=True))
        batch_op.alter_column('payment_method',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.create_unique_constraint(None, ['reference_number'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('payment_method',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.drop_column('payment_details')
        batch_op.drop_column('reference_number')
        batch_op.drop_column('payment_provider')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('shipping_address')

    # ### end Alembic commands ###
