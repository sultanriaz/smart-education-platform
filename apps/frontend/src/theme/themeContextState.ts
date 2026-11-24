import { createContext, useContext } from "react";
import type { PaletteDefinition, PaletteId, ThemeMode } from "./palettes";

export const STORAGE_PALETTE_KEY = "sep-palette";
export const STORAGE_MODE_KEY = "sep-mode";
export const LEGACY_THEME_KEY = "sep-theme";

export interface ThemeContextValue {
  palette: PaletteId;
  mode: ThemeMode;
  activePalette: PaletteDefinition;
  palettes: PaletteDefinition[];
  setPalette: (palette: PaletteId) => void;
  setMode: (mode: ThemeMode) => void;
  toggleMode: () => void;
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return ctx;
}
