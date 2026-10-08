import type { PropsWithChildren, ReactNode } from "react";
import { cn } from "../../lib/cn";

export function Card({
  title,
  description,
  children,
  className
}: PropsWithChildren<{ title?: ReactNode; description?: ReactNode; className?: string }>) {
  return (
    <section className={cn("panel p-5", className)}>
      {title ? (
        <div className="mb-4">
          <h2 className="text-base font-semibold text-ink">{title}</h2>
          {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}
