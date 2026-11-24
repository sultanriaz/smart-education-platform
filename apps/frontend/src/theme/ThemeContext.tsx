import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import {
  DEFAULT_PALETTE,
  PALETTE_MAP,
  PALETTES,
  isValidMode,
  isValidPalette,
  type PaletteId,
  type ThemeMode,
} from "./palettes";
import {
  LEGACY_THEME_KEY,
  STORAGE_MODE_KEY,
  STORAGE_PALETTE_KEY,
  ThemeContext,
  type ThemeContextValue,
} from "./themeContextState";

function resolveInitialPalette(): PaletteId {
  if (typeof document !== "undefined") {
    const attr = document.documentElement.dataset.palette;
    if (isValidPalette(attr)) return attr;
  }
  try {
    const stored = localStorage.getItem(STORAGE_PALETTE_KEY);
    if (isValidPalette(stored)) return stored;
  } catch {
    // ignore storage access issues
  }
  return DEFAULT_PALETTE;
}

function getSystemMode(): ThemeMode {
  if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "light";
}

function resolveInitialMode(): ThemeMode {
  if (typeof document !== "undefined") {
    const attr = document.documentElement.dataset.mode;
    if (isValidMode(attr)) return attr;
  }
  try {
    const stored = localStorage.getItem(STORAGE_MODE_KEY);
    if (isValidMode(stored)) return stored;
    const legacy = localStorage.getItem(LEGACY_THEME_KEY);
    if (isValidMode(legacy)) return legacy;
  } catch {
    // ignore storage access issues
  }
  return getSystemMode();
}

function applyThemeToRoot(palette: PaletteId, mode: ThemeMode) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.palette = palette;
  root.dataset.mode = mode;
  root.dataset.theme = mode;
  root.style.colorScheme = mode;
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [palette, setPaletteState] = useState<PaletteId>(resolveInitialPalette);
  const [mode, setModeState] = useState<ThemeMode>(resolveInitialMode);

  useEffect(() => {
    applyThemeToRoot(palette, mode);
    if (typeof document !== "undefined") {
      // Enable smooth color transitions only after initial mount completes
      requestAnimationFrame(() => {
        document.documentElement.dataset.themeReady = "true";
      });
    }
  }, [palette, mode]);

  // Keep default mode synced with system preference ONLY while user hasn't saved a manual mode choice
  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (event: MediaQueryListEvent) => {
      try {
        if (!localStorage.getItem(STORAGE_MODE_KEY) && !localStorage.getItem(LEGACY_THEME_KEY)) {
          setModeState(event.matches ? "dark" : "light");
        }
      } catch {
        setModeState(event.matches ? "dark" : "light");
      }
    };
    media.addEventListener?.("change", onChange);
    return () => media.removeEventListener?.("change", onChange);
  }, []);

  const setPalette = useCallback((next: PaletteId) => {
    setPaletteState(next);
    try {
      localStorage.setItem(STORAGE_PALETTE_KEY, next);
    } catch {
      // ignore storage quota / privacy restrictions
    }
  }, []);

  const setMode = useCallback((next: ThemeMode) => {
    setModeState(next);
    try {
      localStorage.setItem(STORAGE_MODE_KEY, next);
      localStorage.setItem(LEGACY_THEME_KEY, next);
    } catch {
      // ignore
    }
  }, []);

  const toggleMode = useCallback(() => {
    setMode(mode === "dark" ? "light" : "dark");
  }, [mode, setMode]);

  const value = useMemo<ThemeContextValue>(
    () => ({
      palette,
      mode,
      activePalette: PALETTE_MAP[palette] ?? PALETTE_MAP[DEFAULT_PALETTE],
      palettes: PALETTES,
      setPalette,
      setMode,
      toggleMode,
    }),
    [palette, mode, setPalette, setMode, toggleMode]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
