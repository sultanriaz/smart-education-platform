import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, beforeEach } from "vitest";
import { DynamicSpaceFinder } from "./DynamicSpaceFinder";

describe("DynamicSpaceFinder", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("removes AC/Room Equipment/Today's Slots/Free Until and keeps consistent Block B count when switching blocks", () => {
    render(
      <MemoryRouter>
        <DynamicSpaceFinder mode="teacher" />
      </MemoryRouter>
    );

    // Removed legacy filters and metadata
    expect(screen.queryByText("Air Conditioned")).not.toBeInTheDocument();
    expect(screen.queryByText("High-Density Wi-Fi")).not.toBeInTheDocument();
    expect(screen.queryByText("Room Equipment")).not.toBeInTheDocument();
    expect(screen.queryByText("Today's Slots")).not.toBeInTheDocument();
    expect(screen.queryByText("Free Until")).not.toBeInTheDocument();

    // Replacement labels present
    expect(screen.getAllByText("Availability").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Capacity").length).toBeGreaterThan(0);

    // Block B tab count remains identical whether All Blocks or Block B is active
    const blockBTabBefore = screen.getByRole("button", { name: /^Block B/i });
    const countBefore = blockBTabBefore.textContent?.match(/\d+/)?.[0];
    fireEvent.click(blockBTabBefore);
    const blockBTabAfter = screen.getByRole("button", { name: /^Block B/i });
    const countAfter = blockBTabAfter.textContent?.match(/\d+/)?.[0];
    expect(countBefore).toBeDefined();
    expect(countAfter).toBe(countBefore);
  });

  it("opens the room reservation form inline right at the clicked card without a top overlay", () => {
    render(
      <MemoryRouter>
        <DynamicSpaceFinder mode="teacher" />
      </MemoryRouter>
    );

    const bookButtons = screen.getAllByRole("button", { name: /Book for Makeup Lecture/i });
    expect(bookButtons.length).toBeGreaterThan(0);
    fireEvent.click(bookButtons[0]!);

    expect(screen.getByRole("button", { name: /Confirm Booking/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Makeup Lecture/i)).toBeInTheDocument();
  });
});
