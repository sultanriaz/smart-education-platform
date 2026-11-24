import { AppErrorBoundary } from "./AppErrorBoundary";
import { AppProviders } from "./AppProviders";
import { AppRouter } from "./AppRouter";
import { ThemeSwitcherFab } from "../components/theme/ThemeSwitcherFab";

export function App() {
  return (
    <AppErrorBoundary>
      <AppProviders>
        <AppRouter />
        <ThemeSwitcherFab />
      </AppProviders>
    </AppErrorBoundary>
  );
}
