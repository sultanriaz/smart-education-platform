import { render, screen, fireEvent, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { TimetableHub } from "./TimetableHub";

function renderHub(initialRole: "student" | "teacher" = "student") {
  return render(
    <MemoryRouter>
      <TimetableHub initialRole={initialRole} />
    </MemoryRouter>
  );
}

describe("TimetableHub", () => {
  it("renders Student and Teacher options, simple English controls, and BCS-7C schedule by default", () => {
    renderHub();

    const roleGroup = screen.getByRole("group", { name: "Choose schedule view" });
    expect(within(roleGroup).getByRole("button", { name: /^Student/i })).toHaveAttribute("aria-pressed", "true");
    expect(within(roleGroup).getByRole("button", { name: /^Teacher/i })).toHaveAttribute("aria-pressed", "false");

    // Simple English controls with only ONE calendar save button
    expect(screen.getByRole("button", { name: "List View" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Table View" })).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Save Calendar" })).toHaveLength(1);

    // No technical jargon visible
    expect(screen.queryByText(/Matrix/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Export \.ics/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Occupancy/i)).not.toBeInTheDocument();

    // Default section and lectures count
    expect(screen.getByRole("button", { name: "BCS-7C" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("9 lectures a week")).toBeInTheDocument();
    expect(screen.getAllByText("Compiler Construction").length).toBeGreaterThan(0);

    // Room change notice explicitly mentions the day and class
    expect(screen.getByText(/Room Change Notice \(Tuesday/i)).toBeInTheDocument();
  });

  it("switches sections cleanly and updates lecture counts", () => {
    renderHub();

    fireEvent.click(screen.getByRole("button", { name: "BCS-7A" }));
    expect(screen.getByText("6 lectures a week")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "BCS-7B" }));
    expect(screen.getByText("5 lectures a week")).toBeInTheDocument();
  });

  it("shows Sir Munir Wednesday Slot 2 BCS-7C class and includes Engr. Bilal Khan in Teacher view", () => {
    renderHub("teacher");

    const select = screen.getByLabelText("Teacher:") as HTMLSelectElement;
    expect(select.value).toBe("Sir Munir (Dr. Munir Ahmad)");

    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toContain("Engr. Bilal Khan");

    // Sir Munir has BCS-7C on Wednesday in Slot 2
    const wednesdaySection = screen.getByRole("region", { name: "Wednesday classes" });
    expect(wednesdaySection).toHaveTextContent("Compiler Construction");
    expect(wednesdaySection).toHaveTextContent("BCS-7C");
    expect(wednesdaySection).toHaveTextContent("Slot 2");
    expect(wednesdaySection).toHaveTextContent("Room C-204");
  });

  it("filters classes by search and shows empty state reset when no match exists", () => {
    renderHub();

    const searchInput = screen.getByPlaceholderText("Search classes...");
    fireEvent.change(searchInput, { target: { value: "Database" } });
    expect(screen.getAllByText(/Database Systems/).length).toBeGreaterThan(0);

    fireEvent.change(searchInput, { target: { value: "NonExistentClass999" } });
    expect(screen.getByText(/No classes matched/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clear Search" }));
    expect(screen.getByText("9 lectures a week")).toBeInTheDocument();
  });

  it("switches to Table View cleanly with full teacher names and opens details popup", () => {
    renderHub();

    fireEvent.click(screen.getByRole("button", { name: "Table View" }));
    expect(screen.getByText("Weekly Class Table")).toBeInTheDocument();
    // Only one Save Calendar button still
    expect(screen.getAllByRole("button", { name: "Save Calendar" })).toHaveLength(1);
    // Full teacher name, never truncated to "Dr. Muhammad"
    expect(screen.getAllByText("Dr. Muhammad Asim").length).toBeGreaterThan(0);

    // Click a class in the table to open details modal
    const compilerButtons = screen.getAllByRole("button", { name: /Compiler Construction/i });
    fireEvent.click(compilerButtons[0]!);

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(dialog).toHaveTextContent("Classroom Location");
    expect(dialog).toHaveTextContent("Add to Google Calendar");

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
