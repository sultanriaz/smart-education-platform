"""Persist the earlier of the quiz timer and assignment deadline."""

import sqlalchemy as sa
from alembic import op

revision = "0004_attempt_expiry"
down_revision = "0003_assessment_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("attempts", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(
        """UPDATE attempts AS a SET expires_at = LEAST(
            qa.due_at,
            CASE WHEN q.duration_minutes IS NOT NULL
                 THEN a.started_at + q.duration_minutes * INTERVAL '1 minute'
                 ELSE qa.due_at END
        ) FROM quiz_assignments AS qa JOIN quizzes AS q ON q.id = qa.quiz_id
        WHERE qa.id = a.assignment_id"""
    )
    op.create_index("ix_attempts_status_expiry", "attempts", ["status", "expires_at"])


def downgrade():
    op.drop_index("ix_attempts_status_expiry", table_name="attempts")
    op.drop_column("attempts", "expires_at")
