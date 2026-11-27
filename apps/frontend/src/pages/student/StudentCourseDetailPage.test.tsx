import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthContext, type AuthContextValue } from "../../features/auth/useAuth";
import { StudentCourseDetailPage } from "./StudentCourseDetailPage";

const studentAuth: AuthContextValue = {
  state: "authenticated",
  user: {
    id: "student-155",
    email: "BCS-155",
    fullName: "Student SP23-BCS-155",
    roles: ["student"],
  },
  login: async () => {},
  logout: async () => {},
  reloadUser: async () => {},
};

function renderCourseDetail(courseId = "compiler") {
  return render(
    <AuthContext.Provider value={studentAuth}>
      <MemoryRouter initialEntries={[`/app/student/courses/${courseId}`]}>
        <Routes>
          <Route
            path="/app/student/courses/:courseId"
            element={<StudentCourseDetailPage />}
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  );
}

describe("StudentCourseDetailPage", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("displays course summary, all 10 navigation cards, and 'No Notifications' by default", () => {
    renderCourseDetail("compiler");

    expect(
      screen.getByRole("heading", { name: "Compiler Construction" })
    ).toBeInTheDocument();
    expect(screen.getByText("# CSC441")).toBeInTheDocument();
    expect(screen.getByText("3 Credit Hours")).toBeInTheDocument();
    expect(screen.getByText("Prof. Mr. Bilal")).toBeInTheDocument();

    const expectedLabels = [
      "Notifications",
      "Attendance",
      "Marks",
      "GDB",
      "Assignments",
      "MDB",
      "Lecture Hub",
      "Quizzes",
      "Resources",
      "Course Info",
    ];
    for (const label of expectedLabels) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }

    expect(screen.getByText("No Notifications")).toBeInTheDocument();
  });

  it("switches to Attendance with Class/Lab rings and filters, and shows Course Info syllabus", () => {
    renderCourseDetail("compiler");

    fireEvent.click(screen.getByRole("button", { name: "Attendance" }));
    expect(screen.getByText("Class Attendance")).toBeInTheDocument();
    expect(screen.getByText("Lab Attendance")).toBeInTheDocument();
    expect(screen.getByText("Attendance Type:")).toBeInTheDocument();
    expect(screen.getByText("Start Time")).toBeInTheDocument();
    expect(screen.getByText("End Time")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Present" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Absent" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Late" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Excused" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Lab" }));
    expect(screen.getAllByText("PRESENT").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("ABSENT").length).toBeGreaterThanOrEqual(1);

    fireEvent.click(screen.getAllByRole("button", { name: "All" })[0]!);
    fireEvent.click(screen.getByRole("button", { name: "Absent" }));
    expect(screen.getAllByText("ABSENT").length).toBeGreaterThanOrEqual(1);

    fireEvent.click(screen.getByRole("button", { name: "Course Info" }));
    expect(screen.getByText("Syllabus Topics")).toBeInTheDocument();
    expect(screen.getByText("Course Name")).toBeInTheDocument();
  });

  it("supports Assignment upload and Marks, Resources, GDB, and MDB views inline", () => {
    const createObjectUrlSpy = vi.fn(() => "blob:mock");
    const revokeObjectUrlSpy = vi.fn();
    const anchorClickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {});
    Object.defineProperty(URL, "createObjectURL", {
      writable: true,
      value: createObjectUrlSpy,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      writable: true,
      value: revokeObjectUrlSpy,
    });

    try {
      renderCourseDetail("compiler");

      fireEvent.click(screen.getByRole("button", { name: "Marks" }));
      expect(screen.getByRole("heading", { name: "Marks" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Quizzes" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Assignments" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Mid Term" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Final Term" })).toBeInTheDocument();
      expect(screen.getByText("Quiz 1")).toBeInTheDocument();
      expect(screen.getByText("Ass 1")).toBeInTheDocument();
      expect(screen.queryByText(/Pending/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Upgrade/i)).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "Assignments" }));
      expect(screen.queryByText("Pending")).not.toBeInTheDocument();
      expect(screen.queryByText("Graded")).not.toBeInTheDocument();
      expect(screen.queryByText(/Weightage:/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Marks:/i)).not.toBeInTheDocument();

      const fileInput = screen.getByLabelText("Select assignment file to upload");
      const [firstUpload] = screen.getAllByRole("button", { name: /Upload submission for/i });
      if (!firstUpload) throw new Error("Expected at least one Upload button");
      fireEvent.click(firstUpload);
      const file = new File(["pdf-content"], "solution.pdf", {
        type: "application/pdf",
      });
      fireEvent.change(fileInput, { target: { files: [file] } });
      expect(screen.getByText("Submitted file: solution.pdf")).toBeInTheDocument();

      const [firstDownload] = screen.getAllByRole("button", { name: /Download/i });
      if (!firstDownload) throw new Error("Expected at least one Download button");
      fireEvent.click(firstDownload);
      expect(createObjectUrlSpy).toHaveBeenCalledTimes(1);
      expect(anchorClickSpy).toHaveBeenCalledTimes(1);

      fireEvent.click(screen.getByRole("button", { name: "Quizzes" }));
      expect(screen.queryByText("Graded")).not.toBeInTheDocument();
      expect(screen.queryByText(/Topics:/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Marks:/i)).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "Lecture Hub" }));
      expect(screen.queryByText("Recorded Lectures")).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "Resources" }));
      expect(screen.getByRole("heading", { name: "Resources" })).toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "GDB" }));
      expect(
        screen.getByRole("heading", { name: /Graded Discussion Board/i })
      ).toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "MDB" }));
      expect(
        screen.getByRole("heading", { name: /Moderated Discussion Board/i })
      ).toBeInTheDocument();
    } finally {
      anchorClickSpy.mockRestore();
    }
  });
});
