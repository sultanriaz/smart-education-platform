from __future__ import annotations

import uuid

NAMESPACE = uuid.UUID("11111111-2222-3333-4444-555555555555")


def stable_uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, name)


ADMIN_USER_ID = stable_uuid("admin-user")
TEACHER_USER_ID = stable_uuid("teacher-user")
STUDENT_USER_ID = stable_uuid("student-user")
OTHER_STUDENT_USER_ID = stable_uuid("other-student-user")
DEPARTMENT_ID = stable_uuid("department")
PROGRAM_ID = stable_uuid("program")
SEMESTER_ID = stable_uuid("semester")
COURSE_ID = stable_uuid("course")
SECTION_ID = stable_uuid("section")
ROOM_ID = stable_uuid("room")
