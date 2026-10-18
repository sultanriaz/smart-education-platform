"""Wave 14 idempotent account onboarding receipts. Revision ID: 0006_wave14_user_imports"""
import sqlalchemy as sa
from alembic import op
revision = "0006_wave14_user_imports"
down_revision = "0005_wave13_auth_activity"
branch_labels = depends_on = None

def upgrade():
    op.create_table("identity_import_batches", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("idempotency_key", sa.String(160), unique=True, nullable=False), sa.Column("content_digest", sa.String(64), nullable=False), sa.Column("result", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
def downgrade():
    op.drop_table("identity_import_batches")
