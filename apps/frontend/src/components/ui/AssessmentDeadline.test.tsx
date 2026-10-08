import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { AssessmentDeadline } from "./AssessmentDeadline";

afterEach(() => { cleanup(); vi.useRealTimers(); });

it("counts down to the server deadline and finalizes once across rerenders", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-10-08T10:00:00Z"));
  const onExpire = vi.fn();
  const { rerender } = render(<AssessmentDeadline expiresAt="2026-10-08T10:00:03Z" onExpire={onExpire} />);
  expect(screen.getByRole("timer")).toHaveTextContent("0:03 remaining");
  act(() => vi.advanceTimersByTime(3000));
  expect(onExpire).toHaveBeenCalledTimes(1);
  rerender(<AssessmentDeadline expiresAt="2026-10-08T10:00:03Z" onExpire={() => onExpire()} />);
  act(() => vi.advanceTimersByTime(1000));
  expect(onExpire).toHaveBeenCalledTimes(1);
});

it("finalizes an already expired resumed attempt immediately", () => {
  const onExpire = vi.fn();
  render(<AssessmentDeadline expiresAt="2000-01-01T00:00:00Z" onExpire={onExpire} />);
  expect(onExpire).toHaveBeenCalledTimes(1);
});

it("uses server time when the student's clock is ahead", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-10-08T11:00:00Z"));
  const onExpire = vi.fn();
  render(<AssessmentDeadline expiresAt="2026-10-08T10:01:00Z" serverTime="2026-10-08T10:00:00Z" onExpire={onExpire} />);
  expect(screen.getByRole("timer")).toHaveTextContent("1:00 remaining");
  expect(onExpire).not.toHaveBeenCalled();
});
