"""Wave10: optional local business hours and requester notes."""
import sqlalchemy as sa
from alembic import op

revision = "0004_wave10_hours_notes"
down_revision = "0003_facility_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("facilities", sa.Column("opens_at_local", sa.Time(), nullable=True))
    op.add_column("facilities", sa.Column("closes_at_local", sa.Time(), nullable=True))
    op.add_column("facilities", sa.Column("operating_timezone", sa.String(64), nullable=False, server_default="UTC"))
    op.add_column("bookings", sa.Column("requester_note", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("bookings", "requester_note")
    for column in ("operating_timezone", "closes_at_local", "opens_at_local"):
        op.drop_column("facilities", column)
