import { useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import * as api from "../../features/admin/admin-api";
import {
  adminKeys,
  useAcademicYears,
  useAdminMutation,
  useCourses,
  useDepartments,
  useEnrollments,
  usePrograms,
  useSections,
  useSemesters,
  useStudentProfiles,
  useTeacherProfiles,
  useTeachingAssignments
} from "../../features/admin/hooks";

export function AdminAcademicPage() {
  const departments = useDepartments();
  const programs = usePrograms();
  const years = useAcademicYears();
  const semesters = useSemesters();
  const courses = useCourses();
  const sections = useSections();
  const students = useStudentProfiles();
  const teachers = useTeacherProfiles();
  const enrollments = useEnrollments();
  const teaching = useTeachingAssignments();
  const toast = useToast();

  const createDepartment = useAdminMutation(api.createDepartment, adminKeys.departments);
  const createProgram = useAdminMutation(api.createProgram, adminKeys.programs);
  const createYear = useAdminMutation(api.createAcademicYear, adminKeys.years);
  const createSemester = useAdminMutation(api.createSemester, adminKeys.semesters);
  const createCourse = useAdminMutation(api.createCourse, adminKeys.courses);
  const createSection = useAdminMutation(api.createSection, adminKeys.sections);
  const createStudent = useAdminMutation(api.createStudentProfile, adminKeys.studentProfiles);
  const createTeacher = useAdminMutation(api.createTeacherProfile, adminKeys.teacherProfiles);
  const createEnrollment = useAdminMutation(api.createEnrollment, adminKeys.enrollments);
  const createTeaching = useAdminMutation(api.createTeachingAssignment, adminKeys.teachingAssignments);

  const [departmentForm, setDepartmentForm] = useState({ code: "", name: "" });
  const [programForm, setProgramForm] = useState({ code: "", name: "", department_id: "" });
  const [yearForm, setYearForm] = useState({ name: "", starts_on: "", ends_on: "" });
  const [semesterForm, setSemesterForm] = useState({
    name: "",
    academic_year_id: "",
    starts_on: "",
    ends_on: ""
  });
  const [courseForm, setCourseForm] = useState({
    code: "",
    title: "",
    department_id: "",
    credit_hours: 3
  });
  const [sectionForm, setSectionForm] = useState({
    name: "",
    course_id: "",
    semester_id: "",
    program_id: "",
    capacity: 40
  });
  const [studentForm, setStudentForm] = useState({
    identity_user_id: "",
    student_id: "",
    program_id: "",
    batch: ""
  });
  const [teacherForm, setTeacherForm] = useState({
    identity_user_id: "",
    employee_id: "",
    department_id: ""
  });
  const [enrollmentForm, setEnrollmentForm] = useState({
    student_user_id: "",
    section_id: ""
  });
  const [assignmentForm, setAssignmentForm] = useState({
    teacher_user_id: "",
    section_id: ""
  });

  const allQueries = [
    departments, programs, years, semesters, courses, sections,
    students, teachers, enrollments, teaching
  ];

  if (allQueries.some((query) => query.isLoading)) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading academic administration…" />
      </div>
    );
  }

  if (allQueries.some((query) => query.error)) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Academic setup" />
        <InlineError message="Academic master data could not be loaded. The merge pass must reconcile Sprint 2 route/schema names with this Admin adapter." />
      </div>
    );
  }

  async function perform<T>(action: () => Promise<T>, success: string) {
    try {
      await action();
      toast.push(success, "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Academic operation failed.", "error");
    }
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Academic setup"
        description="Manage departments, programs, academic years, semesters, courses, sections, academic profiles, enrollments, and Teacher assignments."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Departments & programs">
          <form
            className="grid gap-3 sm:grid-cols-[1fr_2fr_auto]"
            onSubmit={(event: FormEvent) => {
              event.preventDefault();
              void perform(
                () => createDepartment.mutateAsync(departmentForm),
                "Department created."
              ).then(() => setDepartmentForm({ code: "", name: "" }));
            }}
          >
            <Input
              label="Department code"
              value={departmentForm.code}
              onChange={(e) => setDepartmentForm((f) => ({ ...f, code: e.target.value }))}
            />
            <Input
              label="Department name"
              value={departmentForm.name}
              onChange={(e) => setDepartmentForm((f) => ({ ...f, name: e.target.value }))}
            />
            <Button className="self-end" type="submit">Add</Button>
          </form>

          <form
            className="mt-6 grid gap-3 sm:grid-cols-2"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () => createProgram.mutateAsync(programForm),
                "Program created."
              ).then(() => setProgramForm({ code: "", name: "", department_id: "" }));
            }}
          >
            <Input
              label="Program code"
              value={programForm.code}
              onChange={(e) => setProgramForm((f) => ({ ...f, code: e.target.value }))}
            />
            <Input
              label="Program name"
              value={programForm.name}
              onChange={(e) => setProgramForm((f) => ({ ...f, name: e.target.value }))}
            />
            <label className="block text-sm font-medium sm:col-span-2">
              Department
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={programForm.department_id}
                onChange={(e) =>
                  setProgramForm((f) => ({ ...f, department_id: e.target.value }))
                }
              >
                <option value="">Select department</option>
                {(departments.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.code} · {item.name}
                  </option>
                ))}
              </select>
            </label>
            <Button type="submit">Add program</Button>
          </form>

          <div className="mt-5 flex flex-wrap gap-2">
            {(departments.data ?? []).map((item) => (
              <Badge key={item.id}>{item.code} · {item.name}</Badge>
            ))}
          </div>
        </Card>

        <Card title="Academic years & semesters">
          <form
            className="grid gap-3 sm:grid-cols-3"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () => createYear.mutateAsync(yearForm),
                "Academic year created."
              ).then(() =>
                setYearForm({ name: "", starts_on: "", ends_on: "" })
              );
            }}
          >
            <Input
              label="Year name"
              value={yearForm.name}
              onChange={(e) => setYearForm((f) => ({ ...f, name: e.target.value }))}
            />
            <Input
              label="Starts"
              type="date"
              value={yearForm.starts_on}
              onChange={(e) => setYearForm((f) => ({ ...f, starts_on: e.target.value }))}
            />
            <Input
              label="Ends"
              type="date"
              value={yearForm.ends_on}
              onChange={(e) => setYearForm((f) => ({ ...f, ends_on: e.target.value }))}
            />
            <Button type="submit">Add academic year</Button>
          </form>

          <form
            className="mt-6 grid gap-3 sm:grid-cols-2"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () => createSemester.mutateAsync(semesterForm),
                "Semester created."
              ).then(() =>
                setSemesterForm({
                  name: "",
                  academic_year_id: "",
                  starts_on: "",
                  ends_on: ""
                })
              );
            }}
          >
            <Input
              label="Semester name"
              value={semesterForm.name}
              onChange={(e) => setSemesterForm((f) => ({ ...f, name: e.target.value }))}
            />
            <label className="block text-sm font-medium">
              Academic year
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={semesterForm.academic_year_id}
                onChange={(e) =>
                  setSemesterForm((f) => ({ ...f, academic_year_id: e.target.value }))
                }
              >
                <option value="">Select year</option>
                {(years.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <Input
              label="Starts"
              type="date"
              value={semesterForm.starts_on}
              onChange={(e) => setSemesterForm((f) => ({ ...f, starts_on: e.target.value }))}
            />
            <Input
              label="Ends"
              type="date"
              value={semesterForm.ends_on}
              onChange={(e) => setSemesterForm((f) => ({ ...f, ends_on: e.target.value }))}
            />
            <Button type="submit">Add semester</Button>
          </form>
        </Card>

        <Card title="Courses">
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () =>
                  createCourse.mutateAsync({
                    code: courseForm.code,
                    title: courseForm.title,
                    department_id: courseForm.department_id || undefined,
                    credit_hours: courseForm.credit_hours
                  }),
                "Course created."
              ).then(() =>
                setCourseForm({
                  code: "",
                  title: "",
                  department_id: "",
                  credit_hours: 3
                })
              );
            }}
          >
            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Course code"
                value={courseForm.code}
                onChange={(e) => setCourseForm((f) => ({ ...f, code: e.target.value }))}
              />
              <Input
                label="Course title"
                value={courseForm.title}
                onChange={(e) => setCourseForm((f) => ({ ...f, title: e.target.value }))}
              />
            </div>
            <label className="block text-sm font-medium">
              Department
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={courseForm.department_id}
                onChange={(e) =>
                  setCourseForm((f) => ({ ...f, department_id: e.target.value }))
                }
              >
                <option value="">Optional department</option>
                {(departments.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Input
              label="Credit hours"
              type="number"
              min={1}
              max={12}
              value={courseForm.credit_hours}
              onChange={(e) =>
                setCourseForm((f) => ({
                  ...f,
                  credit_hours: Number(e.target.value) || 1
                }))
              }
            />
            <Button type="submit">Add course</Button>
          </form>

          <div className="mt-5 max-h-56 overflow-auto rounded-xl border border-line">
            {(courses.data ?? []).map((item) => (
              <div key={item.id} className="border-b border-line/70 px-3 py-2 text-sm">
                <span className="font-semibold">{item.code}</span> · {item.title}
              </div>
            ))}
          </div>
        </Card>

        <Card title="Sections">
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () =>
                  createSection.mutateAsync({
                    name: sectionForm.name,
                    course_id: sectionForm.course_id,
                    semester_id: sectionForm.semester_id,
                    program_id: sectionForm.program_id || undefined,
                    capacity: sectionForm.capacity
                  }),
                "Section created."
              ).then(() =>
                setSectionForm({
                  name: "",
                  course_id: "",
                  semester_id: "",
                  program_id: "",
                  capacity: 40
                })
              );
            }}
          >
            <Input
              label="Section name"
              value={sectionForm.name}
              onChange={(e) => setSectionForm((f) => ({ ...f, name: e.target.value }))}
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm font-medium">
                Course
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={sectionForm.course_id}
                  onChange={(e) =>
                    setSectionForm((f) => ({ ...f, course_id: e.target.value }))
                  }
                >
                  <option value="">Select course</option>
                  {(courses.data ?? []).map((item) => (
                    <option key={item.id} value={item.id}>{item.code} · {item.title}</option>
                  ))}
                </select>
              </label>
              <label className="block text-sm font-medium">
                Semester
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={sectionForm.semester_id}
                  onChange={(e) =>
                    setSectionForm((f) => ({ ...f, semester_id: e.target.value }))
                  }
                >
                  <option value="">Select semester</option>
                  {(semesters.data ?? []).map((item) => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
              </label>
            </div>
            <label className="block text-sm font-medium">
              Program
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={sectionForm.program_id}
                onChange={(e) =>
                  setSectionForm((f) => ({ ...f, program_id: e.target.value }))
                }
              >
                <option value="">Optional program</option>
                {(programs.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Input
              label="Capacity"
              type="number"
              min={1}
              value={sectionForm.capacity}
              onChange={(e) =>
                setSectionForm((f) => ({
                  ...f,
                  capacity: Number(e.target.value) || 1
                }))
              }
            />
            <Button type="submit">Add section</Button>
          </form>
        </Card>

        <Card title="Student & Teacher profiles">
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () =>
                  createStudent.mutateAsync({
                    identity_user_id: studentForm.identity_user_id,
                    student_id: studentForm.student_id,
                    program_id: studentForm.program_id || undefined,
                    batch: studentForm.batch || undefined
                  }),
                "Student academic profile created."
              ).then(() =>
                setStudentForm({
                  identity_user_id: "",
                  student_id: "",
                  program_id: "",
                  batch: ""
                })
              );
            }}
          >
            <h3 className="font-semibold">Student profile</h3>
            <Input
              label="Identity user UUID"
              value={studentForm.identity_user_id}
              onChange={(e) => setStudentForm((f) => ({ ...f, identity_user_id: e.target.value }))}
            />
            <Input
              label="Student ID"
              value={studentForm.student_id}
              onChange={(e) => setStudentForm((f) => ({ ...f, student_id: e.target.value }))}
            />
            <label className="block text-sm font-medium">
              Program
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={studentForm.program_id}
                onChange={(e) => setStudentForm((f) => ({ ...f, program_id: e.target.value }))}
              >
                <option value="">Optional program</option>
                {(programs.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Input
              label="Batch / cohort"
              value={studentForm.batch}
              onChange={(e) => setStudentForm((f) => ({ ...f, batch: e.target.value }))}
            />
            <Button type="submit">Create student profile</Button>
          </form>

          <form
            className="mt-6 space-y-3 border-t border-line pt-6"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () =>
                  createTeacher.mutateAsync({
                    identity_user_id: teacherForm.identity_user_id,
                    employee_id: teacherForm.employee_id,
                    department_id: teacherForm.department_id || undefined
                  }),
                "Teacher academic profile created."
              ).then(() =>
                setTeacherForm({
                  identity_user_id: "",
                  employee_id: "",
                  department_id: ""
                })
              );
            }}
          >
            <h3 className="font-semibold">Teacher profile</h3>
            <Input
              label="Identity user UUID"
              value={teacherForm.identity_user_id}
              onChange={(e) => setTeacherForm((f) => ({ ...f, identity_user_id: e.target.value }))}
            />
            <Input
              label="Employee ID"
              value={teacherForm.employee_id}
              onChange={(e) => setTeacherForm((f) => ({ ...f, employee_id: e.target.value }))}
            />
            <label className="block text-sm font-medium">
              Department
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={teacherForm.department_id}
                onChange={(e) => setTeacherForm((f) => ({ ...f, department_id: e.target.value }))}
              >
                <option value="">Optional department</option>
                {(departments.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Button type="submit">Create Teacher profile</Button>
          </form>
        </Card>

        <Card title="Enrollment & teaching assignment">
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () => createEnrollment.mutateAsync(enrollmentForm),
                "Student enrolled."
              ).then(() =>
                setEnrollmentForm({ student_user_id: "", section_id: "" })
              );
            }}
          >
            <h3 className="font-semibold">Enroll Student</h3>
            <label className="block text-sm font-medium">
              Student
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={enrollmentForm.student_user_id}
                onChange={(e) =>
                  setEnrollmentForm((f) => ({ ...f, student_user_id: e.target.value }))
                }
              >
                <option value="">Select Student</option>
                {(students.data ?? []).map((item) => (
                  <option key={item.id} value={item.identityUserId}>
                    {item.studentId} · {item.identityUserId}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium">
              Section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={enrollmentForm.section_id}
                onChange={(e) =>
                  setEnrollmentForm((f) => ({ ...f, section_id: e.target.value }))
                }
              >
                <option value="">Select section</option>
                {(sections.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <Button type="submit">Enroll Student</Button>
          </form>

          <form
            className="mt-6 space-y-3 border-t border-line pt-6"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () => createTeaching.mutateAsync(assignmentForm),
                "Teacher assigned to section."
              ).then(() =>
                setAssignmentForm({ teacher_user_id: "", section_id: "" })
              );
            }}
          >
            <h3 className="font-semibold">Assign Teacher</h3>
            <label className="block text-sm font-medium">
              Teacher
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={assignmentForm.teacher_user_id}
                onChange={(e) =>
                  setAssignmentForm((f) => ({ ...f, teacher_user_id: e.target.value }))
                }
              >
                <option value="">Select Teacher</option>
                {(teachers.data ?? []).map((item) => (
                  <option key={item.id} value={item.identityUserId}>
                    {item.employeeId} · {item.identityUserId}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium">
              Section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={assignmentForm.section_id}
                onChange={(e) =>
                  setAssignmentForm((f) => ({ ...f, section_id: e.target.value }))
                }
              >
                <option value="">Select section</option>
                {(sections.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <Button type="submit">Assign Teacher</Button>
          </form>
        </Card>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-2">
        <Card title="Current sections">
          <div className="max-h-80 overflow-auto">
            {(sections.data ?? []).map((item) => (
              <div key={item.id} className="border-b border-line/70 px-2 py-3 text-sm">
                <span className="font-semibold">{item.name}</span>
                <span className="ml-2 text-muted">
                  course {item.courseId} · semester {item.semesterId}
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Current assignments">
          <div className="max-h-80 overflow-auto text-sm">
            {(teaching.data ?? []).map((item) => (
              <div key={item.id} className="border-b border-line/70 px-2 py-3">
                Teacher {item.teacherUserId} → Section {item.sectionId}
              </div>
            ))}
            {(enrollments.data ?? []).map((item) => (
              <div key={item.id} className="border-b border-line/70 px-2 py-3">
                Student {item.studentUserId} → Section {item.sectionId} · {item.status}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
