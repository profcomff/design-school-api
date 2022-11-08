from alembic import op
import sqlalchemy as sa


revision = 'c54ae0974f75'
down_revision = 'd124a172c3b3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE "user" ALTER COLUMN year TYPE varchar(10) USING year::varchar(6);')


def downgrade():
    op.execute('DELETE FROM "response" WHERE user_id IN (SELECT id FROM "user" WHERE LENGTH(year) > 6) RETURNING *')
    op.execute('DELETE FROM "user" WHERE LENGTH(year) > 6')
    op.execute('ALTER TABLE "user" ALTER COLUMN year TYPE varchar(6) USING year::varchar(10);')
