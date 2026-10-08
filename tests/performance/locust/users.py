from __future__ import annotations

from locust import task

from common import BearerUser, env, json_env


class StudentUser(BearerUser):
    weight = 75
    token_env = "SMARTEDU_STUDENT_TOKEN"
    credential_prefix = "SMARTEDU_PERF_STUDENT"

    @task(10)
    def academic_context(self):
        self.get_json(
            env("PERF_STUDENT_ACADEMIC_PATH", "/api/v1/academic/students/me/sections"),
            name="student.academic_context",
        )

    @task(15)
    def timetable(self):
        self.get_json(
            env("PERF_STUDENT_SCHEDULE_PATH", "/api/v1/scheduling/timetable/me"),
            name="schedule.read",
        )

    @task(15)
    def attendance(self):
        self.get_json(
            env("PERF_STUDENT_ATTENDANCE_PATH", "/api/v1/attendance/students/me/attendance"),
            name="attendance.read",
        )

    @task(10)
    def notifications(self):
        self.get_json(
            env("PERF_STUDENT_NOTIFICATIONS_PATH", "/api/v1/notifications/notifications"),
            name="notifications.inbox",
        )

    @task(20)
    def resources(self):
        self.get_json(
            env("PERF_STUDENT_RESOURCES_PATH", "/api/v1/learning/students/me/resources"),
            name="learning.resources",
        )

    @task(15)
    def assessments(self):
        self.get_json(
            env("PERF_STUDENT_ASSESSMENTS_PATH", "/api/v1/assessments/students/me/assignments"),
            name="assessment.read",
        )

    @task(5)
    def facilities(self):
        self.get_json(
            env("PERF_STUDENT_FACILITIES_PATH", "/api/v1/facilities/facilities"),
            name="facility.read",
        )

    @task(10)
    def reporting(self):
        self.get_json(
            env("PERF_STUDENT_REPORT_PATH", "/api/v1/attendance/students/me/attendance/summary"),
            name="attendance.summary",
        )


class TeacherUser(BearerUser):
    weight = 20
    token_env = "SMARTEDU_TEACHER_TOKEN"
    credential_prefix = "SMARTEDU_PERF_TEACHER"

    @task(15)
    def sections(self):
        self.get_json(
            env("PERF_TEACHER_SECTIONS_PATH", "/api/v1/academic/sections"),
            name="teacher.sections",
        )

    @task(20)
    def attendance(self):
        self.get_json(
            env("PERF_TEACHER_ATTENDANCE_PATH", "/api/v1/attendance/sessions"),
            name="attendance.read",
        )

    @task(10)
    def schedule(self):
        self.get_json(
            env("PERF_TEACHER_SCHEDULE_PATH", "/api/v1/scheduling/timetable/me"),
            name="schedule.read",
        )

    @task(15)
    def learning(self):
        self.get_json(
            env("PERF_TEACHER_RESOURCES_PATH", "/api/v1/learning/resources"),
            name="learning.resources",
        )

    @task(20)
    def assessments(self):
        self.get_json(
            env("PERF_TEACHER_ASSESSMENTS_PATH", "/api/v1/assessments/teachers/me/quizzes"),
            name="assessment.read",
        )

    @task(10)
    def notifications(self):
        self.get_json(
            env("PERF_TEACHER_NOTIFICATIONS_PATH", "/api/v1/notifications/notifications"),
            name="notifications.inbox",
        )

    @task(10)
    def reporting(self):
        self.get_json(
            env("PERF_TEACHER_REPORT_PATH", "/api/v1/attendance/sessions"),
            name="attendance.read",
        )


class AdminUser(BearerUser):
    weight = 5
    token_env = "SMARTEDU_ADMIN_TOKEN"
    credential_prefix = "SMARTEDU_PERF_ADMIN"

    @task(15)
    def academic(self):
        self.get_json(
            env("PERF_ADMIN_ACADEMIC_PATH", "/api/v1/academic/sections"),
            name="admin.academic",
        )

    @task(15)
    def schedule(self):
        self.get_json(
            env("PERF_ADMIN_SCHEDULE_PATH", "/api/v1/scheduling/schedules"),
            name="schedule.read",
        )

    @task(10)
    def facilities(self):
        self.get_json(
            env("PERF_ADMIN_FACILITIES_PATH", "/api/v1/facilities/bookings"),
            name="facility.read",
        )

    @task(30)
    def reporting(self):
        self.get_json(
            env("PERF_ADMIN_REPORT_PATH", "/api/v1/reporting/dashboard/overview"),
            name="reporting.dashboard",
        )

    @task(20)
    def platform(self):
        self.get_json(
            env("PERF_ADMIN_PLATFORM_PATH", "/api/v1/platform/admin/audit"),
            name="platform.audit",
        )

    @task(10)
    def notifications(self):
        self.get_json(
            env("PERF_ADMIN_NOTIFICATIONS_PATH", "/api/v1/notifications/notifications"),
            name="notifications.inbox",
        )


class AttendanceMutationUser(BearerUser):
    """
    Optional dedicated attendance-write workload.

    Enable with `--class-picker` interactively or explicitly select this class
    on the Locust CLI after configuring path/payload environment variables.
    """
    weight = 0
    token_env = "SMARTEDU_TEACHER_TOKEN"
    credential_prefix = "SMARTEDU_PERF_TEACHER"
    wait_time = lambda _self: 1.0

    @task
    def mark_attendance(self):
        path = env("PERF_ATTENDANCE_WRITE_PATH")
        if not path:
            return
        payload = json_env("PERF_ATTENDANCE_WRITE_PAYLOAD")
        self.mutate_json(
            "POST",
            path,
            name="attendance.mark",
            payload=payload,
        )


class GenericMutationUser(BearerUser):
    """
    Optional mutation benchmark for one idempotent endpoint.

    Configure:
      PERF_MUTATION_PATH
      PERF_MUTATION_METHOD
      PERF_MUTATION_PAYLOAD
      PERF_MUTATION_NAME
      PERF_MUTATION_TOKEN_ENV (defaults to Admin token)
    """
    weight = 0
    token_env = "SMARTEDU_ADMIN_TOKEN"
    credential_prefix = "SMARTEDU_PERF_ADMIN"

    def on_start(self) -> None:
        dynamic_token_env = env(
            "PERF_MUTATION_TOKEN_ENV",
            "SMARTEDU_ADMIN_TOKEN",
        )
        self.token_env = dynamic_token_env
        super().on_start()

    @task
    def mutate(self):
        path = env("PERF_MUTATION_PATH")
        if not path:
            return
        self.mutate_json(
            env("PERF_MUTATION_METHOD", "POST").upper(),
            path,
            name=env("PERF_MUTATION_NAME", "general.mutation"),
            payload=json_env("PERF_MUTATION_PAYLOAD"),
        )
