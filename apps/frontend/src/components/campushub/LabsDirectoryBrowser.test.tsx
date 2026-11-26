import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LabsDirectoryBrowser } from "./LabsDirectoryBrowser";

describe("LabsDirectoryBrowser", () => {
  it("renders Labs Directory header, search bar, 7 labs count, and stacked lab cards matching screenshot", () => {
    render(<LabsDirectoryBrowser />);

    expect(screen.getByRole("heading", { name: "Labs Directory" })).toBeInTheDocument();
    expect(screen.getByText("All campus laboratories")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search labs or location...")).toBeInTheDocument();
    expect(screen.getByText("7 LABS FOUND")).toBeInTheDocument();

    // Primary labs visible with clean locations
    expect(screen.getByRole("button", { name: /C Lab - 6/i })).toHaveTextContent("C Block (1st Floor)");
    expect(screen.getByRole("button", { name: /C Lab - 8/i })).toHaveTextContent("A Block (G Floor)");
    expect(screen.getByRole("button", { name: /Physics Lab/i })).toHaveTextContent("A Block (2nd Floor)");
    expect(screen.getByRole("button", { name: /Biosciences Lab/i })).toHaveTextContent("B Block (1st Floor)");
    expect(screen.getByRole("button", { name: /Chemistry Lab/i })).toHaveTextContent("A Block (1st Floor)");
  });

  it("filters labs by search query and block menu options, and clears filters", () => {
    render(<LabsDirectoryBrowser />);

    const searchInput = screen.getByPlaceholderText("Search labs or location...");
    fireEvent.change(searchInput, { target: { value: "Physics" } });
    expect(screen.getByText("1 LAB FOUND")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Physics Lab/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clear lab search" }));
    expect(screen.getByText("7 LABS FOUND")).toBeInTheDocument();

    // Open block filter menu
    fireEvent.click(screen.getByLabelText("Filter labs by block"));
    fireEvent.click(screen.getByRole("button", { name: "B Block" }));
    expect(screen.getByText("2 LABS FOUND")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Biosciences Lab/i })).toBeInTheDocument();
  });

  it("opens clean lab details dialog when clicking a lab card and closes on button click", () => {
    render(<LabsDirectoryBrowser />);

    fireEvent.click(screen.getByRole("button", { name: /C Lab - 6/i }));
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("C Block (1st Floor)");
    expect(dialog).toHaveTextContent("50 Computers");

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
