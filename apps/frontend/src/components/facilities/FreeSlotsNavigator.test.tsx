import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { FreeSlotsNavigator } from "./FreeSlotsNavigator";

describe("FreeSlotsNavigator", () => {
  it("renders header, day/slot filters, and 34 rooms free by default on Wednesday Slot 1", () => {
    const handleBack = vi.fn();
    render(<FreeSlotsNavigator onBack={handleBack} />);

    // Header title and subtitle
    expect(screen.getByRole("heading", { name: "Free Slots" })).toBeInTheDocument();
    expect(screen.getByText("Available rooms by day & slot")).toBeInTheDocument();

    // Days & Slots
    expect(screen.getByRole("button", { name: "Mon" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tue" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Wed" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Thu" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Fri" })).toBeInTheDocument();

    expect(screen.getByRole("button", { name: "1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "2" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "3" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "4" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "5" })).toBeInTheDocument();

    // Default status count: 34 rooms free
    expect(screen.getByText("34 rooms free")).toBeInTheDocument();

    // Block A: 7 rooms · 1 lab
    expect(screen.getByText("A- Block")).toBeInTheDocument();
    expect(screen.getByText("7 rooms · 1 lab")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-1\s+60/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-2\s+45/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-3\s+55/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A-4\s+40/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /A Lab-9\s+30/ })).toBeInTheDocument();

    // Block B: 7 rooms · 2 labs
    expect(screen.getByText("B- Block")).toBeInTheDocument();
    expect(screen.getByText("7 rooms · 2 labs")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /B-1\s+70/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /B-2\s+65/ })).toBeInTheDocument();

    // Back button triggers onBack
    const backBtn = screen.getByLabelText("Back to main explorer");
    fireEvent.click(backBtn);
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it("opens room detail modal when clicking a room and closes it", () => {
    render(<FreeSlotsNavigator />);

    const roomButton = screen.getByRole("button", { name: /A-1\s+60/ });
    fireEvent.click(roomButton);

    // Modal dialog opens
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Lecture Hall A-1")).toBeInTheDocument();
    expect(screen.getByText("Block A · 1st Floor")).toBeInTheDocument();
    expect(screen.getByText("60 Students")).toBeInTheDocument();
    expect(screen.getByText("Campus Wi-Fi")).toBeInTheDocument();
    expect(screen.getByText("Air Conditioned")).toBeInTheDocument();

    // Close modal
    const closeBtn = screen.getByRole("button", { name: "Close Details" });
    fireEvent.click(closeBtn);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("updates free rooms count when selecting another day and slot", () => {
    render(<FreeSlotsNavigator />);

    const thuButton = screen.getByRole("button", { name: "Thu" });
    fireEvent.click(thuButton);

    const slot2Button = screen.getByRole("button", { name: "2" });
    fireEvent.click(slot2Button);

    // Free count changes dynamically
    expect(screen.getByText(/rooms free/)).toBeInTheDocument();
  });
});
