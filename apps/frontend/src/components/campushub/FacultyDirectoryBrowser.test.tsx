import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { FacultyDirectoryBrowser } from "./FacultyDirectoryBrowser";

describe("FacultyDirectoryBrowser", () => {
  it("matches the Faculty & Teachers overview with 4 Offices and Quick Access cards", () => {
    const handleBack = vi.fn();
    render(<FacultyDirectoryBrowser onBack={handleBack} />);

    expect(screen.getByRole("heading", { name: "Faculty & Teachers" })).toBeInTheDocument();
    expect(screen.getByText("Campus administrative offices")).toBeInTheDocument();
    expect(screen.getByText("4 Offices")).toBeInTheDocument();
    expect(screen.getByText("QUICK ACCESS")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: "Director" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "HODs" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Teachers" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Batch Advisors" })).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it("opens HODs Directory matching screenshot and supports search & office details modal", () => {
    render(<FacultyDirectoryBrowser />);

    fireEvent.click(screen.getByRole("button", { name: "HODs" }));
    expect(screen.getByRole("heading", { name: "HODs Directory" })).toBeInTheDocument();
    expect(screen.getByText("Heads of Departments")).toBeInTheDocument();
    expect(screen.getByText("8 HODS FOUND")).toBeInTheDocument();
    expect(screen.getByText("Computer Science")).toBeInTheDocument();
    expect(screen.getByText("Food Science")).toBeInTheDocument();
    expect(screen.getByText("Chemistry")).toBeInTheDocument();
    expect(screen.getByText("Civil Engineering")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Search by Department or Name..."), {
      target: { value: "Food" }
    });
    expect(screen.getByText("1 HOD FOUND")).toBeInTheDocument();
    expect(screen.getByText("Dr. Ahmed Bilal")).toBeInTheDocument();
    expect(screen.queryByText("Dr. Ali Raza")).not.toBeInTheDocument();

    // Tapping an HOD card opens full office details modal, Escape closes
    fireEvent.click(screen.getByRole("button", { name: /Dr. Ahmed Bilal/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Faculty & Teachers"));
    expect(screen.getByText("4 Offices")).toBeInTheDocument();
  });

  it("opens Teachers screen with 72 Total Teachers, 2 Categories, and renders Lecturers / PHD Faculty inline below when clicked", () => {
    render(<FacultyDirectoryBrowser />);

    fireEvent.click(screen.getByRole("button", { name: "Teachers" }));
    expect(screen.getByRole("heading", { name: "Teachers" })).toBeInTheDocument();
    expect(screen.getByText("Faculty offices & staff directory")).toBeInTheDocument();
    expect(screen.getByText("2 Categories")).toBeInTheDocument();
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByText("Total Teachers")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lecturers" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "PHD Faculty" })).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Search by teacher or department")).not.toBeInTheDocument();

    // Click Lecturers -> stays on Teachers screen and reveals 10 Members list below
    fireEvent.click(screen.getByRole("button", { name: "Lecturers" }));
    expect(screen.getByText("Total Teachers")).toBeInTheDocument();
    expect(screen.getByText("10 Members")).toBeInTheDocument();
    expect(screen.getByText("10 results")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search by teacher or department")).toBeInTheDocument();
    expect(screen.getByText("Mr. Bilal Shabir Qaisar")).toBeInTheDocument();
    expect(screen.getByText("Ms. Ayesha Tariq")).toBeInTheDocument();

    // Search filters teachers cleanly
    fireEvent.change(screen.getByPlaceholderText("Search by teacher or department"), {
      target: { value: "Software Engineering" }
    });
    expect(screen.getByText("1 result")).toBeInTheDocument();
    expect(screen.getByText("Ms. Ayesha Tariq")).toBeInTheDocument();

    // Clicking PHD Faculty switches the inline list below on the same screen
    fireEvent.click(screen.getByRole("button", { name: "PHD Faculty" }));
    expect(screen.getByText("6 Members")).toBeInTheDocument();
    expect(screen.getByText("Dr. Ayesha Malik")).toBeInTheDocument();

    // Tapping a teacher opens office details modal -> Request Meeting -> Escape closes
    fireEvent.click(screen.getByRole("button", { name: /Dr. Ayesha Malik/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Request Meeting" }));
    expect(screen.getByLabelText(/What would you like to discuss/i)).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens Director and Batch Advisors matching screenshot UI", () => {
    render(<FacultyDirectoryBrowser />);

    fireEvent.click(screen.getByRole("button", { name: "Director" }));
    expect(screen.getByText("Prof. Dr. Saleem Farooq Shaukat")).toBeInTheDocument();
    expect(screen.getByText(/Room A-301 \(Directorate Wing\)/i)).toBeInTheDocument();
    expect(screen.getByText(/director@cuisahiwal\.edu\.pk/i)).toBeInTheDocument();
    expect(screen.getByText(/Condensed Matter Physics/i)).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Back to Faculty & Teachers"));

    fireEvent.click(screen.getByRole("button", { name: "Batch Advisors" }));
    expect(screen.getByRole("heading", { name: "Batch Advisors" })).toBeInTheDocument();
    expect(screen.getByText("Find your batch advisor")).toBeInTheDocument();
    expect(screen.getByText("6 Batches")).toBeInTheDocument();
    expect(screen.getByText("DIRECTORY")).toBeInTheDocument();
    expect(screen.getByText("6 entries")).toBeInTheDocument();
    expect(screen.getByText("Mr. Arslan Sarwar")).toBeInTheDocument();
    expect(screen.getByText("SP23-BCS")).toBeInTheDocument();
    expect(screen.getByText("Dr. Ahmed Sarwar")).toBeInTheDocument();
    expect(screen.getByText("Fa24-BCS")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Search by Teacher or Batch"), {
      target: { value: "Fa24-BCS" }
    });
    expect(screen.getByText("1 entry")).toBeInTheDocument();
    expect(screen.getByText("Dr. Ahmed Sarwar")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Dr. Ahmed Sarwar/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
