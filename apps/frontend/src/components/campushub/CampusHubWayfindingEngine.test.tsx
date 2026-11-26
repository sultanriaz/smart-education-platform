import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { CampusHubWayfindingEngine } from "./CampusHubWayfindingEngine";

describe("CampusHubWayfindingEngine", () => {
  it("shows only the Campus Portal hero and the 6 minimal cards on initial load", () => {
    const handleBack = vi.fn();
    render(<CampusHubWayfindingEngine onBack={handleBack} />);

    expect(screen.getByRole("heading", { name: "Campus Portal" })).toBeInTheDocument();
    expect(screen.getByText("Quick Access")).toBeInTheDocument();
    expect(screen.getByText("6 modules")).toBeInTheDocument();

    // All 6 cards present cleanly
    expect(screen.getByRole("button", { name: "Class Rooms" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Labs Directory" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Faculty & Teachers" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Offices Directory" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Library System" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Statistics" })).toBeInTheDocument();

    // Nothing displayed below (no Faculty directory / blueprints / extra card subtitles)
    expect(screen.queryByText("Interactive Floor Blueprints")).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/Search faculty/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Director, HODs/i)).not.toBeInTheDocument();
    expect(screen.queryByText("56 Rooms")).not.toBeInTheDocument();

    // Top-left back button works
    fireEvent.click(screen.getByLabelText("Back to Main Dashboard"));
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it("opens the next page when a card is clicked instead of showing it below, and returns on Back", () => {
    render(<CampusHubWayfindingEngine />);

    // Open Class Rooms
    fireEvent.click(screen.getByRole("button", { name: "Class Rooms" }));
    expect(screen.queryByText("Quick Access")).not.toBeInTheDocument();
    expect(screen.getByText("SELECT A BLOCK TO VIEW CLASSROOMS")).toBeInTheDocument();

    // Return to Campus Portal
    fireEvent.click(screen.getByRole("button", { name: /Back to Campus Portal/i }));
    expect(screen.getByText("Quick Access")).toBeInTheDocument();

    // Open Labs Directory
    fireEvent.click(screen.getByRole("button", { name: "Labs Directory" }));
    expect(screen.queryByText("Quick Access")).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Labs Directory" })).toBeInTheDocument();

    // Return to Campus Portal
    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(screen.getByText("Quick Access")).toBeInTheDocument();

    // Open Faculty & Teachers -> displays 4 Offices Quick Access cards
    fireEvent.click(screen.getByRole("button", { name: "Faculty & Teachers" }));
    expect(screen.queryByText("6 modules")).not.toBeInTheDocument();
    expect(screen.getByText("4 Offices")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Director" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "HODs" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Teachers" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Batch Advisors" })).toBeInTheDocument();

    // Open Teachers -> displays 2 Categories summary screen, clicking Lecturers reveals list below on same screen
    fireEvent.click(screen.getByRole("button", { name: "Teachers" }));
    expect(screen.getByText("2 Categories")).toBeInTheDocument();
    expect(screen.getByText("Total Teachers")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Lecturers" }));
    expect(screen.getByText("10 Members")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search by teacher or department")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Faculty & Teachers"));
    expect(screen.getByText("4 Offices")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(screen.getByText("Quick Access")).toBeInTheDocument();
    expect(screen.getByText("6 modules")).toBeInTheDocument();

    // Open Offices Directory -> shows 2-card selector screen
    fireEvent.click(screen.getByRole("button", { name: "Offices Directory" }));
    expect(screen.getByRole("heading", { name: "Offices Directory" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Faculty Offices" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Administrative Offices" })).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(screen.getByText("6 modules")).toBeInTheDocument();

    // Open Library System -> shows only library location & block name on the next screen
    fireEvent.click(screen.getByRole("button", { name: "Library System" }));
    expect(screen.getByRole("heading", { name: "Library System" })).toBeInTheDocument();
    expect(screen.getByText("Block Name")).toBeInTheDocument();
    expect(screen.getByText("D Block")).toBeInTheDocument();
    expect(screen.getByText("Library Location")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/Search digital book catalog/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(screen.getByText("6 modules")).toBeInTheDocument();
  });
});
