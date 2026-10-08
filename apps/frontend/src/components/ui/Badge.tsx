import type { PropsWithChildren } from "react";

export function Badge({ children }: PropsWithChildren) {
  return (
    <span className="inline-flex rounded-full bg-surface px-2.5 py-1 text-xs font-semibold text-muted">
      {children}
    </span>
  );
}
