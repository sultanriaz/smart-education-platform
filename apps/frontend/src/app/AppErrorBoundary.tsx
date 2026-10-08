import { Component, type ErrorInfo, type ReactNode } from "react";

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
        <main className="flex min-h-screen items-center justify-center p-6">
          <section className="panel max-w-xl p-8 text-center">
            <h1 className="text-2xl font-bold">Something went wrong</h1>
            <p className="mt-3 text-sm leading-6 text-muted">
              Reload the application. If the problem continues, contact support.
            </p>
            <button
              className="mt-6 rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white"
              onClick={() => window.location.reload()}
            >
              Reload application
            </button>
          </section>
        </main>
      );
    }
    return this.props.children;
  }
}
