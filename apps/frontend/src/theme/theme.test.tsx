import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ThemeSwitcherFab } from "../components/theme/ThemeSwitcherFab";
import { AuthContext, type AuthContextValue } from "../features/auth/useAuth";
import { CampusExplorerPage } from "../pages/CampusExplorerPage";
import { FacultyLoginPage } from "../pages/FacultyLoginPage";
import { ForbiddenPage } from "../pages/ForbiddenPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { RegisterPage } from "../pages/RegisterPage";
import { StudentLoginPage } from "../pages/StudentLoginPage";
import {
  PALETTES,
  PALETTE_MAP,
  isValidMode,
  isValidPalette,
  type PaletteId,
  type ThemeMode,
} from "./palettes";
import { ThemeProvider } from "./ThemeContext";
import {
  STORAGE_MODE_KEY,
  STORAGE_PALETTE_KEY,
  useTheme,
} from "./themeContextState";

function hexToRgb(hex: string): [number, number, number] {
  const clean = hex.replace("#", "");
  return [
    parseInt(clean.slice(0, 2), 16),
    parseInt(clean.slice(2, 4), 16),
    parseInt(clean.slice(4, 6), 16),
  ];
}

function channelLuminance(channel: number): number {
  const c = channel / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex);
  return 0.2126 * channelLuminance(r) + 0.7152 * channelLuminance(g) + 0.0722 * channelLuminance(b);
}

function contrastRatio(fgHex: string, bgHex: string): number {
  const l1 = relativeLuminance(fgHex);
  const l2 = relativeLuminance(bgHex);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function mockMatchMedia(prefersDark: boolean) {
  const listeners = new Set<(event: MediaQueryListEvent) => void>();
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes("prefers-color-scheme: dark") ? prefersDark : false,
      media: query,
      onchange: null,
      addEventListener: (_: string, cb: (event: MediaQueryListEvent) => void) => {
        listeners.add(cb);
      },
      removeEventListener: (_: string, cb: (event: MediaQueryListEvent) => void) => {
        listeners.delete(cb);
      },
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  return {
    triggerChange(nextDark: boolean) {
      for (const cb of listeners) {
        cb({ matches: nextDark } as MediaQueryListEvent);
      }
    },
  };
}

function ThemeProbe() {
  const { palette, mode, activePalette, setPalette, setMode, toggleMode } = useTheme();
  return (
    <div>
      <span data-testid="probe-palette">{palette}</span>
      <span data-testid="probe-mode">{mode}</span>
      <span data-testid="probe-name">{activePalette.name}</span>
      <button type="button" onClick={() => setPalette("natural")}>
        Pick Natural
      </button>
      <button type="button" onClick={() => setMode("dark")}>
        Set Dark
      </button>
      <button type="button" onClick={toggleMode}>
        Toggle Mode
      </button>
    </div>
  );
}

describe("Theme Palettes & WCAG AA Contrast", () => {
  it("defines strictly the 5 specified palettes with light and dark tokens and swatches", () => {
    const ids = PALETTES.map((p) => p.id);
    expect(ids).toEqual(["university", "editorial", "premium", "minimal", "natural"]);

    expect(PALETTE_MAP.university.swatches.light).toEqual({
      primary: "#142B4A",
      secondary: "#159E91",
      accent: "#F2B84B",
      background: "#F5F7FA",
    });
    expect(PALETTE_MAP.editorial.swatches.light).toEqual({
      primary: "#C8372D",
      secondary: "#2B2B2B",
      accent: "#8C8478",
      background: "#F4F1EA",
    });
    expect(PALETTE_MAP.premium.swatches.light).toEqual({
      primary: "#2A2622",
      secondary: "#8A7350",
      accent: "#CDB98F",
      background: "#F5F2EC",
    });
    expect(PALETTE_MAP.minimal.swatches.light).toEqual({
      primary: "#111111",
      secondary: "#8A8A8A",
      accent: "#D4D4D4",
      background: "#F2F2F2",
    });
    expect(PALETTE_MAP.natural.swatches.light).toEqual({
      primary: "#4E6B4A",
      secondary: "#283328",
      accent: "#8FA67F",
      background: "#F3F0E6",
    });

    expect(isValidPalette("university")).toBe(true);
    expect(isValidPalette("ocean")).toBe(false);
    expect(isValidMode("light")).toBe(true);
    expect(isValidMode("dark")).toBe(true);
    expect(isValidMode("sepia")).toBe(false);
  });

  it("passes WCAG AA (>= 4.5:1) contrast on every foreground/background pair across all 5 palettes x 2 modes", () => {
    const failures: string[] = [];
    const modes: ThemeMode[] = ["light", "dark"];

    for (const def of PALETTES) {
      for (const mode of modes) {
        const t = def.modes[mode];
        const pairs: Array<[string, string, string]> = [
          ["textPrimary on background", t.textPrimary, t.background],
          ["textPrimary on surface", t.textPrimary, t.surface],
          ["textPrimary on surfaceAlt", t.textPrimary, t.surfaceAlt],
          ["textSecondary on background", t.textSecondary, t.background],
          ["textSecondary on surface", t.textSecondary, t.surface],
          ["textSecondary on surfaceAlt", t.textSecondary, t.surfaceAlt],
          ["primaryForeground on primary", t.primaryForeground, t.primary],
          ["primaryForeground on primaryHover", t.primaryForeground, t.primaryHover],
          ["primaryInk on background", t.primaryInk, t.background],
          ["primaryInk on surface", t.primaryInk, t.surface],
          ["primaryInk on primarySoft", t.primaryInk, t.primarySoft],
          ["secondaryForeground on secondary", t.secondaryForeground, t.secondary],
          ["secondaryInk on background", t.secondaryInk, t.background],
          ["secondaryInk on surface", t.secondaryInk, t.surface],
          ["secondaryInk on secondarySoft", t.secondaryInk, t.secondarySoft],
          ["accentForeground on accent", t.accentForeground, t.accent],
          ["accentInk on background", t.accentInk, t.background],
          ["accentInk on surface", t.accentInk, t.surface],
          ["accentInk on accentSoft", t.accentInk, t.accentSoft],
          ["successForeground on success", t.successForeground, t.success],
          ["successInk on background", t.successInk, t.background],
          ["successInk on surface", t.successInk, t.surface],
          ["successInk on successSoft", t.successInk, t.successSoft],
          ["warningForeground on warning", t.warningForeground, t.warning],
          ["warningInk on background", t.warningInk, t.background],
          ["warningInk on surface", t.warningInk, t.surface],
          ["warningInk on warningSoft", t.warningInk, t.warningSoft],
          ["errorForeground on error", t.errorForeground, t.error],
          ["errorInk on background", t.errorInk, t.background],
          ["errorInk on surface", t.errorInk, t.surface],
          ["errorInk on errorSoft", t.errorInk, t.errorSoft],
          ["heroFg on heroBg", t.heroFg, t.heroBg],
          ["heroMuted on heroBg", t.heroMuted, t.heroBg],
        ];

        for (const [label, fg, bg] of pairs) {
          const ratio = contrastRatio(fg, bg);
          if (ratio < 4.5) {
            failures.push(`${def.id}/${mode} [${label}]: ${fg} on ${bg} => ${ratio.toFixed(2)}:1`);
          }
        }
      }
    }

    expect(failures).toEqual([]);
  });
});

describe("ThemeProvider & ThemeSwitcherFab", () => {
  beforeEach(() => {
    localStorage.clear();
    delete document.documentElement.dataset.palette;
    delete document.documentElement.dataset.mode;
    delete document.documentElement.dataset.theme;
    delete document.documentElement.dataset.themeReady;
    document.documentElement.style.colorScheme = "";
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("follows prefers-color-scheme when no choice is saved in localStorage", () => {
    const media = mockMatchMedia(true);
    render(
      <ThemeProvider>
        <ThemeProbe />
      </ThemeProvider>
    );

    expect(screen.getByTestId("probe-palette")).toHaveTextContent("university");
    expect(screen.getByTestId("probe-mode")).toHaveTextContent("dark");
    expect(document.documentElement.dataset.palette).toBe("university");
    expect(document.documentElement.dataset.mode).toBe("dark");
    expect(document.documentElement.style.colorScheme).toBe("dark");

    act(() => {
      media.triggerChange(false);
    });
    expect(screen.getByTestId("probe-mode")).toHaveTextContent("light");
    expect(document.documentElement.dataset.mode).toBe("light");
  });

  it("restores saved palette and mode from localStorage on mount and updates across switches", () => {
    mockMatchMedia(false);
    localStorage.setItem(STORAGE_PALETTE_KEY, "premium");
    localStorage.setItem(STORAGE_MODE_KEY, "dark");

    const { unmount } = render(
      <ThemeProvider>
        <ThemeProbe />
      </ThemeProvider>
    );

    expect(screen.getByTestId("probe-palette")).toHaveTextContent("premium");
    expect(screen.getByTestId("probe-mode")).toHaveTextContent("dark");
    expect(document.documentElement.dataset.palette).toBe("premium");
    expect(document.documentElement.dataset.mode).toBe("dark");

    fireEvent.click(screen.getByRole("button", { name: "Pick Natural" }));
    fireEvent.click(screen.getByRole("button", { name: "Toggle Mode" }));
    expect(localStorage.getItem(STORAGE_PALETTE_KEY)).toBe("natural");
    expect(localStorage.getItem(STORAGE_MODE_KEY)).toBe("light");

    unmount();
    delete document.documentElement.dataset.palette;
    delete document.documentElement.dataset.mode;

    render(
      <ThemeProvider>
        <ThemeProbe />
      </ThemeProvider>
    );
    expect(screen.getByTestId("probe-palette")).toHaveTextContent("natural");
    expect(screen.getByTestId("probe-mode")).toHaveTextContent("light");
  });

  it("renders a single FAB, opens menu above it with 5 palettes and Light/Night switch, and closes on Escape / outside click / FAB re-click", () => {
    mockMatchMedia(false);
    render(
      <ThemeProvider>
        <ThemeSwitcherFab />
      </ThemeProvider>
    );

    const switchers = screen.getAllByTestId("global-theme-switcher");
    expect(switchers).toHaveLength(1);

    const fab = screen.getByRole("button", { name: "Open theme and palette switcher" });
    expect(fab).toHaveAttribute("aria-expanded", "false");
    expect(fab).toHaveAttribute("aria-haspopup", "dialog");
    expect(fab.className).toContain("h-14");
    expect(fab.className).toContain("w-14");
    expect(fab.className).toContain("rounded-full");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    // Open menu above button
    fireEvent.click(fab);
    const dialog = screen.getByRole("dialog", { name: "Theme and color palette settings" });
    expect(dialog).toBeInTheDocument();
    expect(dialog.className).toContain("bottom-[calc(100%+0.75rem)]");
    expect(fab).toHaveAttribute("aria-expanded", "true");

    // Open palette dropdown
    const dropdownTrigger = screen.getByRole("button", { name: /Color Palette.*University Navy/i });
    expect(dropdownTrigger).toHaveAttribute("aria-haspopup", "listbox");
    fireEvent.click(dropdownTrigger);

    const listbox = screen.getByRole("listbox");
    expect(listbox).toBeInTheDocument();
    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(5);

    const expectedIds: PaletteId[] = ["university", "editorial", "premium", "minimal", "natural"];
    expect(options.length).toBe(expectedIds.length);
    for (const def of PALETTES) {
      expect(listbox).toHaveTextContent(def.name);
    }

    // Select Editorial palette
    fireEvent.click(screen.getByRole("button", { name: /Editorial/i }));
    expect(document.documentElement.dataset.palette).toBe("editorial");
    expect(localStorage.getItem(STORAGE_PALETTE_KEY)).toBe("editorial");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();

    // Switch Light -> Night mode
    const nightBtn = screen.getByRole("radio", { name: /Night/i });
    const lightBtn = screen.getByRole("radio", { name: /Light/i });
    expect(lightBtn).toHaveAttribute("aria-checked", "true");
    fireEvent.click(nightBtn);
    expect(nightBtn).toHaveAttribute("aria-checked", "true");
    expect(document.documentElement.dataset.mode).toBe("dark");
    expect(localStorage.getItem(STORAGE_MODE_KEY)).toBe("dark");

    // Pressing Escape when dropdown is open closes only the dropdown first
    fireEvent.click(screen.getByRole("button", { name: /Color Palette.*Editorial/i }));
    expect(screen.getByRole("listbox")).toBeInTheDocument();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    // Pressing Escape again closes the dialog and restores focus to FAB
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(document.activeElement).toBe(fab);

    // Clicking FAB opens and clicking outside closes
    fireEvent.click(fab);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.mouseDown(document.body);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    // Clicking FAB opens and clicking FAB again closes
    fireEvent.click(fab);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(fab);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("does not duplicate theme switcher controls on pages", () => {
    mockMatchMedia(false);
    const mockAuth: AuthContextValue = {
      state: "anonymous",
      user: null,
      login: vi.fn(),
      logout: vi.fn(),
      reloadUser: vi.fn(),
    };

    const pages = [
      <CampusExplorerPage key="explorer" />,
      <LoginPage key="login" />,
      <StudentLoginPage key="student-login" />,
      <FacultyLoginPage key="faculty-login" />,
      <RegisterPage key="register" />,
      <NotFoundPage key="not-found" />,
      <ForbiddenPage key="forbidden" />,
    ];

    for (const page of pages) {
      const { unmount } = render(
        <AuthContext.Provider value={mockAuth}>
          <ThemeProvider>
            <MemoryRouter>
              {page}
              <ThemeSwitcherFab />
            </MemoryRouter>
          </ThemeProvider>
        </AuthContext.Provider>
      );

      expect(screen.getAllByTestId("global-theme-switcher")).toHaveLength(1);
      expect(
        screen.getAllByRole("button", { name: /theme|palette/i })
      ).toHaveLength(1);
      unmount();
    }
  });
});
