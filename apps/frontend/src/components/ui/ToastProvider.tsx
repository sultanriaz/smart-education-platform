import { ToastContext, type Toast } from "./useToast";
import {
  useCallback,
  useMemo,
  useState,
  type PropsWithChildren
} from "react";

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = useCallback((message: string, tone: Toast["tone"] = "info") => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(
      () => setToasts((current) => current.filter((toast) => toast.id !== id)),
      4000
    );
  }, []);

  const value = useMemo(() => ({ push }), [push]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="fixed bottom-24 right-4 sm:right-6 z-50 flex w-[min(24rem,calc(100%-2rem))] flex-col gap-2"
        aria-live="polite"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`rounded-xl border px-4 py-3 text-sm shadow-panel ${
              toast.tone === "error"
                ? "border-danger/40 bg-danger-soft text-danger-ink"
                : toast.tone === "success"
                ? "border-success/40 bg-success-soft text-success-ink"
                : "border-line bg-panel text-ink"
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
