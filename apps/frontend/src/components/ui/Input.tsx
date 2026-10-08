import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "../../lib/cn";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
  hint?: string;
};

export const Input = forwardRef<HTMLInputElement, Props>(
  ({ label, error, hint, id, className, ...props }, ref) => {
    const inputId = id ?? props.name;
    return (
      <label className="block text-sm font-medium text-ink" htmlFor={inputId}>
        <span>{label}</span>
        <input
          ref={ref}
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          className={cn(
            "mt-2 block w-full rounded-xl border border-line bg-panel px-3 py-2.5 text-sm text-ink placeholder:text-muted/70 focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
            error && "border-danger",
            className
          )}
          {...props}
        />
        {error ? (
          <span id={`${inputId}-error`} className="mt-1 block text-xs text-danger">
            {error}
          </span>
        ) : hint ? (
          <span id={`${inputId}-hint`} className="mt-1 block text-xs text-muted">
            {hint}
          </span>
        ) : null}
      </label>
    );
  }
);
Input.displayName = "Input";
