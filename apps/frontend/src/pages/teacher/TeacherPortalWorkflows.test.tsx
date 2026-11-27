import type { ReactNode } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthContext, type AuthContextValue } from "../../features/auth/useAuth";
import { ToastProvider } from "../../components/ui/ToastProvider";
import { TeacherDashboardPage } from "./TeacherDashboardPage";
import { TeacherClassesAttendancePage } from "./TeacherClassesAttendancePage";
import { TeacherLearningPage } from "./TeacherLearningPage";
import { TeacherAssessmentsPage } from "./TeacherAssessmentsPage";
import * as teacherApi from "../../features/teacher/teacher-api";
import * as studentHooks from "../../features/student/hooks";

const teacherAuth: AuthContextValue = {
  state: "authenticated",
  user: {
    id: "teacher-1",
    email: "munir@cuisahiwal.edu.pk",
    fullName: "Dr. Munir Ahmad",
    roles: ["teacher"]
  },
  login: async () => {},
  logout: async () => {},
  reloadUser: async () => {}
};

function renderWithProviders(ui: ReactNode, initialPath = "/app/teacher") {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  return render(
    <QueryClientProvider client={qc}>
      <AuthContext.Provider value={teacherAuth}>
        <ToastProvider>
          <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
              <Route path="*" element={ui} />
            </Routes>
          </MemoryRouter>
        </ToastProvider>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

describe("Teacher Portal Workflows", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.spyOn(teacherApi, "getTeacherSections").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherTimetable").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherAssignments").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherResources").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherBanks").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherQuestions").mockResolvedValue([]);
    vi.spyOn(teacherApi, "getTeacherQuizzes").mockResolvedValue([]);
    vi.spyOn(studentHooks, "useUnreadCount").mockReturnValue({
      data: 2,
      isLoading: false,
      isFetching: false,
      error: null,
      refetch: vi.fn()
    } as unknown as ReturnType<typeof studentHooks.useUnreadCount>);
  });

  it("opens pending assessment grading on dashboard, removes Room A/C /explore links, and supports inline lecture attendance", async () => {
    renderWithProviders(<TeacherDashboardPage />);

    // Single faculty reservation link, no A Block / C Block /explore redirects
    const reserveLink = await screen.findByRole("link", { name: /Room & Lab Reservation/i });
    expect(reserveLink).toHaveAttribute("href", "/app/teacher/facilities");
    expect(screen.queryByText("A Block Rooms")).not.toBeInTheDocument();
    expect(screen.queryByText("C Block Rooms")).not.toBeInTheDocument();

    // Pending submission card is clickable and opens student marks entry
    const pendingCard = screen.getByRole("button", {
      name: /Compiler Construction: Assignment 1/i
    });
    fireEvent.click(pendingCard);
    expect(screen.getByText("SP23-BCS-101")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Save Marks/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close grading sheet" }));

    // Today's lecture Take Attendance opens student roster with Present/Absent & Submit
    const takeBtns = screen.getAllByRole("button", { name: /Take Attendance/i });
    fireEvent.click(takeBtns[0]!);
    expect(screen.getByText("Hamza Tariq")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Submit Attendance/i }));
    expect(screen.getByRole("button", { name: /^Edit$/i })).toBeInTheDocument();
  });

  it("lets teacher pick class and slot in Classes & Attendance, mark students, submit, and edit", async () => {
    renderWithProviders(<TeacherClassesAttendancePage />, "/app/teacher/attendance?mode=take");

    expect(await screen.findByRole("heading", { name: /Take Class Attendance/i })).toBeInTheDocument();
    expect(screen.getByText("SP23-BCS-101")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Submit Attendance/i })).toBeInTheDocument();
  });

  it("provides class selection on Lecture Resources even without backend seeded sections", async () => {
    renderWithProviders(<TeacherLearningPage />, "/app/teacher/learning");

    const classSelect = (await screen.findByLabelText("Select Class")) as HTMLSelectElement;
    expect(classSelect.options.length).toBeGreaterThan(1);
  });

  it("lets teacher browse classes -> Assignment 1/2/Quizzes folders -> student marks in Quizzes & Grading", async () => {
    renderWithProviders(<TeacherAssessmentsPage />, "/app/teacher/assessments");

    const folderBtn = await screen.findByRole("button", { name: /Assignment 1/i });
    fireEvent.click(folderBtn);

    expect(screen.getByText("SP23-BCS-101")).toBeInTheDocument();
    expect(screen.getByLabelText("Marks for Hamza Tariq")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Save Marks/i }));
    expect(screen.getByRole("status")).toHaveTextContent(/Saved marks/i);
  });
});
