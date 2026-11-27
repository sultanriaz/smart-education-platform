import { Component, type ErrorInfo, type ReactNode } from "react";
import { ServerCrash, RotateCcw, Home } from "lucide-react";

export class AppErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled application error", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="subtle-grid flex min-h-dvh items-center justify-center p-6">
          <section className="panel max-w-lg p-8 text-center shadow-lg">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-danger-soft text-danger-ink">
              <ServerCrash size={32} aria-hidden="true" />
            </div>
            <p className="mt-4 text-xs font-bold tracking-widest text-danger-ink uppercase">
              HTTP 500
            </p>
            <h1 className="mt-2 text-2xl font-bold">Something went wrong</h1>
            <p className="mt-3 text-sm leading-6 text-muted">
              An unexpected interface error occurred. Reload the application or return to Campus Explorer.
            </p>
            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
                onClick={() => window.location.reload()}
              >
                <RotateCcw size={16} aria-hidden="true" />
                <span>Reload application</span>
              </button>
              <a
                href="/"
                className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-line bg-panel px-5 py-2.5 text-sm font-semibold text-ink hover:bg-surface transition"
              >
                <Home size={16} aria-hidden="true" />
                <span>Campus Explorer</span>
              </a>
            </div>
          </section>
        </main>
      );
    }
    return this.props.children;
  }
}
