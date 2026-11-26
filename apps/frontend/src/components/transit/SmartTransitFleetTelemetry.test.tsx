import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SmartTransitFleetTelemetry } from "./SmartTransitFleetTelemetry";

describe("SmartTransitFleetTelemetry", () => {
  it("renders only the 2 Transport Quick Access cards initially", () => {
    const onBack = vi.fn();
    render(<SmartTransitFleetTelemetry onBack={onBack} />);

    expect(screen.getByRole("heading", { name: /Transport/i })).toBeInTheDocument();
    expect(screen.getByText(/2 Options/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Planned Routes/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Shuttle Schedule/i })).toBeInTheDocument();

    // Details are hidden on initial hub screen
    expect(screen.queryByText(/Jeewan City/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Regular Days/i)).not.toBeInTheDocument();
  });

  it("opens Planned Routes and displays bus stop names with timings", () => {
    render(<SmartTransitFleetTelemetry />);

    fireEvent.click(screen.getByRole("button", { name: /Planned Routes/i }));

    expect(screen.getByText("3 Buses")).toBeInTheDocument();
    expect(screen.getByText(/3 buses found/)).toBeInTheDocument();
    expect(screen.getAllByText(/Jeewan City/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/10:00 AM/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Bus 1/i).length).toBeGreaterThanOrEqual(1);
  });

  it("opens Shuttle Schedule, navigates to direction selector, and displays selected direction timings inline", () => {
    render(<SmartTransitFleetTelemetry />);

    fireEvent.click(screen.getByRole("button", { name: /Shuttle Schedule/i }));

    expect(screen.getByText(/4 Routes/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Regular Days/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /During Exams/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /During Ramzan/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /During Sports Week/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /During Ramzan/i }));

    expect(screen.getByText(/SELECT DIRECTION/i)).toBeInTheDocument();
    const fromUniBtn = screen.getByRole("button", { name: /From University/i });
    const toUniBtn = screen.getByRole("button", { name: /To University/i });
    expect(fromUniBtn).toBeInTheDocument();
    expect(toUniBtn).toBeInTheDocument();

    fireEvent.click(fromUniBtn);
    expect(screen.getAllByText(/Bus 1/i).length).toBeGreaterThanOrEqual(1);

    fireEvent.click(toUniBtn);
    expect(screen.getAllByText(/From University|To University/i).length).toBeGreaterThanOrEqual(2);
  });
});
