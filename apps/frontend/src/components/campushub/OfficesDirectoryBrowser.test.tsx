import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { OfficesDirectoryBrowser } from "./OfficesDirectoryBrowser";

describe("OfficesDirectoryBrowser", () => {
  it("matches the Offices Directory selector with Faculty Offices and Administrative Offices cards", () => {
    const handleBack = vi.fn();
    render(<OfficesDirectoryBrowser onBack={handleBack} />);

    expect(screen.getByRole("heading", { name: "Offices Directory" })).toBeInTheDocument();
    expect(screen.getByText("Campus Portal")).toBeInTheDocument();
    expect(screen.getByText("University Directory")).toBeInTheDocument();
    expect(screen.getByText("Select a Directory")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: "Faculty Offices" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Administrative Offices" })).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Back to Campus Portal"));
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it("opens Faculty Offices and minimal Administrative Offices matching screenshots", () => {
    render(<OfficesDirectoryBrowser />);

    // Open Faculty Offices
    fireEvent.click(screen.getByRole("button", { name: "Faculty Offices" }));
    expect(screen.getByRole("heading", { name: "Faculty Offices" })).toBeInTheDocument();
    expect(screen.getByText("DIRECTORY")).toBeInTheDocument();
    expect(screen.getByText("Mr. Bilal Shabir Qaisar")).toBeInTheDocument();

    // Return to Offices Directory -> open Administrative Offices
    fireEvent.click(screen.getByLabelText("Back to Offices Directory"));
    expect(screen.getByText("Select a Directory")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Administrative Offices" }));
    expect(screen.getByRole("heading", { name: "Administrative Offices" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search offices, blocks...")).toBeInTheDocument();
    expect(screen.getByText("6 offices found")).toBeInTheDocument();

    // Minimal cards show name, block-floor, and phone cleanly
    expect(screen.getByText("Admission Office")).toBeInTheDocument();
    expect(screen.getByText("A Block — 1st Floor")).toBeInTheDocument();
    expect(screen.getByText("+92 300 1234567")).toBeInTheDocument();
    expect(screen.getByText("Exam Office")).toBeInTheDocument();
    expect(screen.getByText("Accounts Office")).toBeInTheDocument();
    expect(screen.getByText("Registrar Office")).toBeInTheDocument();

    // Filter by block/name
    fireEvent.change(screen.getByPlaceholderText("Search offices, blocks..."), {
      target: { value: "Admin Block" }
    });
    expect(screen.getByText("1 office found")).toBeInTheDocument();
    expect(screen.getByText("Accounts Office")).toBeInTheDocument();

    // Tap Admin card -> Get Queue Number -> Escape closes
    fireEvent.click(screen.getByRole("button", { name: /Accounts Office/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Get Queue Number" }));
    expect(screen.getByText("Your Queue Number")).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
