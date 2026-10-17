"""Wave 10: campus hierarchy, term lifecycle, and course archive."""
import sqlalchemy as sa
from alembic import op

revision = "0005_wave10_catalog_lifecycle"
down_revision = "0004_identity_lifecycle_inbox"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("campuses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("departments", sa.Column("campus_id", sa.Uuid(), sa.ForeignKey("campuses.id"), nullable=True))
    op.create_index("ix_departments_campus_id", "departments", ["campus_id"])
    op.add_column("semesters", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("courses", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column("courses", "is_archived")
    op.drop_column("semesters", "is_active")
    op.drop_index("ix_departments_campus_id", table_name="departments")
    op.drop_column("departments", "campus_id")
    op.drop_table("campuses")
