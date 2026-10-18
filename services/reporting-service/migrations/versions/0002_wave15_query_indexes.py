"""Wave 15 reporting query index improvements. Revision ID: 0002_wave15_query_indexes"""
from alembic import op
revision = "0002_wave15_query_indexes"
down_revision = "0001_reporting"
branch_labels = depends_on = None
INDEXES = [("ix_reporting_attendance_student_date", "attendance_projection", ["student_user_id", "session_date"]), ("ix_reporting_attendance_section_date", "attendance_projection", ["section_id", "session_date"]), ("ix_reporting_assessment_student_graded", "assessment_projection", ["student_user_id", "graded_at"]), ("ix_reporting_assessment_section_graded", "assessment_projection", ["section_id", "graded_at"]), ("ix_reporting_enrollment_section_status", "enrollment_projection", ["section_id", "status"]), ("ix_reporting_facility_status_updated", "facility_booking_projection", ["status", "updated_at"]), ("ix_reporting_snapshots_actor_created", "report_snapshots", ["generated_by_user_id", "created_at"])]
def upgrade():
    for name, table, cols in INDEXES: op.create_index(name, table, cols)
def downgrade():
    for name, table, _ in reversed(INDEXES): op.drop_index(name, table)
