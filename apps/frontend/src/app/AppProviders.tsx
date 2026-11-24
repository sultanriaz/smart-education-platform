import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type PropsWithChildren } from "react";
import { BrowserRouter } from "react-router-dom";
import { ToastProvider } from "../components/ui/ToastProvider";
import { AuthProvider } from "../features/auth/AuthContext";
import { ThemeProvider } from "../theme/ThemeContext";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: (count, error) => {
              if (
                error &&
                typeof error === "object" &&
                "status" in error &&
                typeof (error as { status?: unknown }).status === "number" &&
                (error as { status: number }).status < 500
              ) {
                return false;
              }
              return count < 2;
            },
            refetchOnWindowFocus: false
          },
          mutations: { retry: false }
        }
      })
  );

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ToastProvider>
            <AuthProvider>{children}</AuthProvider>
          </ToastProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
