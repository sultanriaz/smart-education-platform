import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { BlockClassroomsBrowser } from "./BlockClassroomsBrowser";

describe("BlockClassroomsBrowser", () => {
  it("shows Block A, Block B, and Block C cards initially with classroom counts", () => {
    render(<BlockClassroomsBrowser />);

    expect(screen.getByText("SELECT A BLOCK TO VIEW CLASSROOMS")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Block A/i })).toHaveTextContent("20 Classrooms");
    expect(screen.getByRole("button", { name: /Block B/i })).toHaveTextContent("18 Classrooms");
    expect(screen.getByRole("button", { name: /Block C/i })).toHaveTextContent("18 Classrooms");
  });

  it("displays Block A classrooms floor-wise matching the mobile UI when Block A is selected", () => {
    render(<BlockClassroomsBrowser />);

    fireEvent.click(screen.getByRole("button", { name: /Block A/i }));

    expect(screen.getByRole("heading", { name: "Class Rooms" })).toBeInTheDocument();
    expect(screen.getByText("20 Rooms")).toBeInTheDocument();
    expect(screen.getByText("AVAILABLE ROOMS")).toBeInTheDocument();

    // Floor cards
    expect(screen.getByRole("heading", { name: "G- Floor" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "1st- Floor" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "2nd- Floor" })).toBeInTheDocument();

    // Ground floor rooms A-1..A-7
    expect(screen.getByRole("button", { name: /A-1\s+60/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-7\s+48/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-1\.1\s+70/ })).toBeInTheDocument();

    // Only classrooms (no labs/auditorium)
    expect(screen.queryByText(/\bLabs?\b/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Auditorium/i)).not.toBeInTheDocument();

    // Collapse G- Floor
    const gFloorToggle = screen.getByRole("button", { name: /G- Floor/i });
    fireEvent.click(gFloorToggle);
    expect(screen.queryByRole("button", { name: /A-1\s+60/ })).not.toBeInTheDocument();
  });

  it("switches to Block B and Block C floor-wise views and opens classroom details modal", () => {
    render(<BlockClassroomsBrowser />);

    fireEvent.click(screen.getByRole("button", { name: /Block B/i }));
    expect(screen.getByText("18 Rooms")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "3rd- Floor" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /B-1\s+70/ })).toBeInTheDocument();

    // Switch directly to Block C
    fireEvent.click(screen.getByRole("button", { name: "Block C" }));
    expect(screen.getByRole("button", { name: /C-204\s+60/ })).toBeInTheDocument();

    // Open classroom info dialog
    fireEvent.click(screen.getByRole("button", { name: /C-204\s+60/ }));
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("Block C · 2nd Floor");
    expect(dialog).toHaveTextContent("60 Students");

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    // Back button returns to block cards
    fireEvent.click(screen.getByLabelText("Back to blocks"));
    expect(screen.getByText("SELECT A BLOCK TO VIEW CLASSROOMS")).toBeInTheDocument();
  });
});
