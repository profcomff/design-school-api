from alembic import op


revision = 'd124a172c3b3'
down_revision = '6feaabe4cc2d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, 'user', ['social_web_id'])


def downgrade():
    op.drop_constraint(None, 'user', type_='unique')
