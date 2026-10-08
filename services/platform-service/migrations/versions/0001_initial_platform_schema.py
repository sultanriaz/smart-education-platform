from __future__ import annotations

from alembic import op

revision = "0001_platform"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    from app.db.base import Base

    Base.metadata.create_all(bind=bind)


def downgrade():
    bind = op.get_bind()
    from app.db.base import Base

    Base.metadata.drop_all(bind=bind)
