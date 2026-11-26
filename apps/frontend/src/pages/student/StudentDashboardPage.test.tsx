import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AuthContext, type AuthContextValue } from "../../features/auth/useAuth";
import { StudentDashboardPage } from "./StudentDashboardPage";

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

describe("StudentDashboardPage", () => {
  it("renders the top student header with Profile Photo and only the 6 registered courses with teacher names", () => {
    render(
      <AuthContext.Provider value={studentAuth}>
        <MemoryRouter>
          <StudentDashboardPage />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    expect(
      screen.getByRole("heading", { name: /Welcome: CIIT\/SP23-BCS-155\/SWL/i })
    ).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText("COMSATS University Islamabad")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Upload Profile Photo/i })
    ).toBeInTheDocument();

    expect(screen.getByText("REGISTERED COURSES")).toBeInTheDocument();
    expect(screen.getByText("6 courses")).toBeInTheDocument();

    // All 6 registered courses + teachers
    expect(screen.getByText("Compiler Construction")).toBeInTheDocument();
    expect(screen.getByText("Prof. Mr. Bilal")).toBeInTheDocument();
    expect(screen.getByText("Information Security")).toBeInTheDocument();
    expect(screen.getByText("Dr. Ayesha Malik")).toBeInTheDocument();
    expect(screen.getByText("Machine Learning")).toBeInTheDocument();
    expect(screen.getByText("Discrete Mathematics")).toBeInTheDocument();

    // 6 attendance summary rows
    expect(screen.getAllByText("Attendance summary")).toHaveLength(6);
  });
});
