import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AuthContext, type AuthContextValue } from "../features/auth/useAuth";
import { ThemeProvider } from "../theme/ThemeContext";
import { CampusExplorerPage } from "./CampusExplorerPage";

const guestAuth: AuthContextValue = {
  state: "anonymous",
  user: null,
  login: async () => {},
  logout: async () => {},
  reloadUser: async () => {},
};

function renderExplorer(initialEntry = "/") {
  return render(
    <ThemeProvider>
      <AuthContext.Provider value={guestAuth}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <CampusExplorerPage />
        </MemoryRouter>
      </AuthContext.Provider>
    </ThemeProvider>
  );
}

describe("CampusExplorerPage overview dashboard", () => {
  it("renders Welcome!, COMSATS University Islamabad, Student Portal banner, and only the 7 Quick Access cards", () => {
    renderExplorer("/");

    expect(screen.getByRole("heading", { name: /Welcome!/i })).toBeInTheDocument();
    expect(
      screen.getAllByText(/COMSATS University Islamabad/i).length
    ).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/QUICK ACCESS/i)).toBeInTheDocument();

    // 7 Quick Access items (+ featured Student Portal card)
    expect(screen.getAllByText(/Student Portal/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole("button", { name: /Time Table/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Teachers/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Free Slots/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Campus Hub/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Transport Service/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Sports Week/i })).toBeInTheDocument();

    // Removed legacy extras should not be displayed
    expect(screen.queryByText(/Self Assessment/i)).not.toBeInTheDocument();
  });

  it("opens Teachers directly into the Faculty & Teachers directory", async () => {
    renderExplorer("/explore");

    fireEvent.click(screen.getByRole("button", { name: /Teachers/i }));

    expect(await screen.findByRole("heading", { name: /Faculty & Teachers/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Director/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /HODs/i })).toBeInTheDocument();
  });
});
