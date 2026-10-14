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
  const [programForm, setProgramForm] = useState({ code: "", name: "", department_id: "", duration_semesters: 8 });
  const [yearForm, setYearForm] = useState({ code: "", name: "", starts_on: "", ends_on: "" });
  const [semesterForm, setSemesterForm] = useState({
    name: "",
    academic_year_id: "",
    number: 1,
    starts_on: "",
    ends_on: ""
  });
  const [courseForm, setCourseForm] = useState({
    code: "",
    title: "",
    program_id: "",
    credits: 3,
    semester_number: 1
  });
  const [sectionForm, setSectionForm] = useState({
    code: "",
    course_id: "",
    semester_id: "",
    capacity: 40
  });
  const [studentForm, setStudentForm] = useState({
    external_user_id: "",
    student_number: "",
    program_id: "",
    admission_year_id: "",
    current_semester: 1
  });
  const [teacherForm, setTeacherForm] = useState({
    external_user_id: "",
    employee_number: "",
    department_id: "",
    designation: ""
  });
  const [enrollmentForm, setEnrollmentForm] = useState({
    student_profile_id: "",
    section_id: ""
  });
  const [assignmentForm, setAssignmentForm] = useState({
    teacher_profile_id: "",
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
      return true;
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Academic operation failed.", "error");
      return false;
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
              ).then((ok) => ok && setDepartmentForm({ code: "", name: "" }));
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
              ).then((ok) => ok && setProgramForm({ code: "", name: "", department_id: "", duration_semesters: 8 }));
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
            <Input label="Duration (semesters)" type="number" min={1} max={20}
              value={programForm.duration_semesters}
              onChange={(e) => setProgramForm((f) => ({ ...f, duration_semesters: Number(e.target.value) || 1 }))} />
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
              ).then((ok) => ok &&
                setYearForm({ code: "", name: "", starts_on: "", ends_on: "" })
              );
            }}
          >
            <Input label="Year code" value={yearForm.code}
              onChange={(e) => setYearForm((f) => ({ ...f, code: e.target.value }))} />
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
              ).then((ok) => ok &&
                setSemesterForm({ name: "", academic_year_id: "", number: 1, starts_on: "", ends_on: "" })
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
            <Input label="Semester number" type="number" min={1}
              value={semesterForm.number}
              onChange={(e) => setSemesterForm((f) => ({ ...f, number: Number(e.target.value) || 1 }))} />
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
                    program_id: courseForm.program_id,
                    credits: courseForm.credits,
                    semester_number: courseForm.semester_number
                  }),
                "Course created."
              ).then((ok) => ok &&
                setCourseForm({
                  code: "",
                  title: "",
                  program_id: "",
                  credits: 3,
                  semester_number: 1
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
              Program
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={courseForm.program_id}
                onChange={(e) =>
                  setCourseForm((f) => ({ ...f, program_id: e.target.value }))
                }
              >
                <option value="">Select program</option>
                {(programs.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Input
              label="Credits"
              type="number"
              min={1}
              max={12}
              value={courseForm.credits}
              onChange={(e) =>
                setCourseForm((f) => ({
                  ...f,
                  credits: Number(e.target.value) || 1
                }))
              }
            />
            <Input label="Curriculum semester number" type="number" min={1}
              value={courseForm.semester_number}
              onChange={(e) => setCourseForm((f) => ({ ...f, semester_number: Number(e.target.value) || 1 }))} />
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
                    code: sectionForm.code,
                    course_id: sectionForm.course_id,
                    semester_id: sectionForm.semester_id,
                    capacity: sectionForm.capacity
                  }),
                "Section created."
              ).then((ok) => ok &&
                setSectionForm({
                  code: "",
                  course_id: "",
                  semester_id: "",
                  capacity: 40
                })
              );
            }}
          >
            <Input
              label="Section code"
              value={sectionForm.code}
              onChange={(e) => setSectionForm((f) => ({ ...f, code: e.target.value }))}
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
                    external_user_id: studentForm.external_user_id,
                    student_number: studentForm.student_number,
                    program_id: studentForm.program_id,
                    admission_year_id: studentForm.admission_year_id,
                    current_semester: studentForm.current_semester
                  }),
                "Student academic profile created."
              ).then((ok) => ok &&
                setStudentForm({
                  external_user_id: "",
                  student_number: "",
                  program_id: "",
                  admission_year_id: "",
                  current_semester: 1
                })
              );
            }}
          >
            <h3 className="font-semibold">Student profile</h3>
            <Input
              label="Identity user UUID"
              value={studentForm.external_user_id}
              onChange={(e) => setStudentForm((f) => ({ ...f, external_user_id: e.target.value }))}
            />
            <Input
              label="Student ID"
              value={studentForm.student_number}
              onChange={(e) => setStudentForm((f) => ({ ...f, student_number: e.target.value }))}
            />
            <label className="block text-sm font-medium">
              Program
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={studentForm.program_id}
                onChange={(e) => setStudentForm((f) => ({ ...f, program_id: e.target.value }))}
              >
                <option value="">Select program</option>
                {(programs.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium">Admission academic year
              <select className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={studentForm.admission_year_id}
                onChange={(e) => setStudentForm((f) => ({ ...f, admission_year_id: e.target.value }))}>
                <option value="">Select admission year</option>
                {(years.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
            </label>
            <Input label="Current semester" type="number" min={1}
              value={studentForm.current_semester}
              onChange={(e) => setStudentForm((f) => ({ ...f, current_semester: Number(e.target.value) || 1 }))} />
            <Button type="submit">Create student profile</Button>
          </form>

          <form
            className="mt-6 space-y-3 border-t border-line pt-6"
            onSubmit={(event) => {
              event.preventDefault();
              void perform(
                () =>
                  createTeacher.mutateAsync({
                    external_user_id: teacherForm.external_user_id,
                    employee_number: teacherForm.employee_number,
                    department_id: teacherForm.department_id,
                    designation: teacherForm.designation
                  }),
                "Teacher academic profile created."
              ).then((ok) => ok &&
                setTeacherForm({
                  external_user_id: "",
                  employee_number: "",
                  department_id: "",
                  designation: ""
                })
              );
            }}
          >
            <h3 className="font-semibold">Teacher profile</h3>
            <Input
              label="Identity user UUID"
              value={teacherForm.external_user_id}
              onChange={(e) => setTeacherForm((f) => ({ ...f, external_user_id: e.target.value }))}
            />
            <Input
              label="Employee ID"
              value={teacherForm.employee_number}
              onChange={(e) => setTeacherForm((f) => ({ ...f, employee_number: e.target.value }))}
            />
            <label className="block text-sm font-medium">
              Department
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={teacherForm.department_id}
                onChange={(e) => setTeacherForm((f) => ({ ...f, department_id: e.target.value }))}
              >
                <option value="">Select department</option>
                {(departments.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.code} · {item.name}</option>
                ))}
              </select>
            </label>
            <Input label="Designation" value={teacherForm.designation}
              onChange={(e) => setTeacherForm((f) => ({ ...f, designation: e.target.value }))} />
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
              ).then((ok) => ok &&
                setEnrollmentForm({ student_profile_id: "", section_id: "" })
              );
            }}
          >
            <h3 className="font-semibold">Enroll Student</h3>
            <label className="block text-sm font-medium">
              Student
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={enrollmentForm.student_profile_id}
                onChange={(e) =>
                  setEnrollmentForm((f) => ({ ...f, student_profile_id: e.target.value }))
                }
              >
                <option value="">Select Student</option>
                {(students.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
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
              ).then((ok) => ok &&
                setAssignmentForm({ teacher_profile_id: "", section_id: "" })
              );
            }}
          >
            <h3 className="font-semibold">Assign Teacher</h3>
            <label className="block text-sm font-medium">
              Teacher
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={assignmentForm.teacher_profile_id}
                onChange={(e) =>
                  setAssignmentForm((f) => ({ ...f, teacher_profile_id: e.target.value }))
                }
              >
                <option value="">Select Teacher</option>
                {(teachers.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
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
