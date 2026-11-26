import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarqueeEventsPortal } from "./MarqueeEventsPortal";

describe("MarqueeEventsPortal", () => {
  it("renders Sports Week schedule with Fall 2026 badge, day tabs, and 11 Monday events", () => {
    render(<MarqueeEventsPortal />);

    expect(screen.getByRole("heading", { name: /Sports Week/i })).toBeInTheDocument();
    expect(screen.getByText(/Fall 2026/i)).toBeInTheDocument();
    expect(screen.getByText(/11 events found/i)).toBeInTheDocument();
    expect(screen.getByText("Cricket Match")).toBeInTheDocument();
    expect(screen.getAllByText(/7:30 AM/i).length).toBeGreaterThanOrEqual(1);
    expect(
      screen.getAllByText(/Sports Ground - Main Pitch/i).length
    ).toBeGreaterThanOrEqual(1);
  });

  it("filters events by search query and switches weekday tabs", () => {
    render(<MarqueeEventsPortal />);

    const searchInput = screen.getByPlaceholderText(/Search by location, game, or time/i);
    fireEvent.change(searchInput, { target: { value: "Cricket" } });
    expect(screen.getByText("Cricket Match")).toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: "" } });
    fireEvent.click(screen.getByRole("tab", { name: /^tue$/i }));
    expect(screen.getByText(/events found/i)).toBeInTheDocument();
  });
});
