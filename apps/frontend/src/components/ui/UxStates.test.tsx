import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { Button } from "./Button";
import { EmptyState } from "./EmptyState";
import { InlineError } from "./InlineError";
import { Input } from "./Input";
import { NotFoundPage } from "../../pages/NotFoundPage";
import { ServerErrorPage } from "../../pages/ServerErrorPage";

describe("UX states and fallback primitives", () => {
  it("renders InlineError with accessible retry action", () => {
    const onRetry = vi.fn();
    render(<InlineError message="Network failed" onRetry={onRetry} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Network failed");
    const retryBtn = screen.getByRole("button", { name: /Retry/i });
    expect(retryBtn).toHaveClass("min-h-11");
    fireEvent.click(retryBtn);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("enforces minimum touch target height on Button and non-zoom Input sizing", () => {
    render(
      <div>
        <Input label="Student Email" type="email" autoComplete="email" />
        <Button>Submit</Button>
        <EmptyState title="Nothing here" description="No items recorded." />
      </div>
    );

    const input = screen.getByLabelText("Student Email");
    expect(input).toHaveClass("min-h-11", "text-base");
    expect(screen.getByRole("button", { name: "Submit" })).toHaveClass("min-h-11");
    expect(screen.getByRole("heading", { name: "Nothing here" })).toBeInTheDocument();
  });

  it("renders HTTP 404 and HTTP 500 fallback pages with working navigation", () => {
    const onRetry = vi.fn();
    render(
      <MemoryRouter>
        <NotFoundPage />
        <ServerErrorPage onRetry={onRetry} />
      </MemoryRouter>
    );

    expect(screen.getByText("HTTP 404")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Return to Dashboard/i })).toHaveAttribute("href", "/app");
    expect(screen.getByText("HTTP 500")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Try Again/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
