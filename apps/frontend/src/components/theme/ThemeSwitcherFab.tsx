import { useEffect, useId, useRef, useState } from "react";
import { Check, ChevronDown, Moon, Palette, Sun, X } from "lucide-react";
import { useTheme } from "../../theme/themeContextState";
import type { PaletteDefinition, PaletteId, ThemeMode } from "../../theme/palettes";

function SwatchPreview({
  definition,
  mode,
}: {
  definition: PaletteDefinition;
  mode: ThemeMode;
}) {
  const s = definition.swatches[mode];
  return (
    <span className="inline-flex items-center gap-1 shrink-0" aria-hidden="true">
      <span
        className="h-3.5 w-3.5 rounded-full border border-line/70 shadow-2xs"
        style={{ backgroundColor: s.primary }}
        title={`Primary: ${s.primary}`}
      />
      <span
        className="h-3.5 w-3.5 rounded-full border border-line/70 shadow-2xs"
        style={{ backgroundColor: s.secondary }}
        title={`Secondary: ${s.secondary}`}
      />
      <span
        className="h-3.5 w-3.5 rounded-full border border-line/70 shadow-2xs"
        style={{ backgroundColor: s.accent }}
        title={`Accent: ${s.accent}`}
      />
      <span
        className="h-3.5 w-3.5 rounded-full border border-line/70 shadow-2xs"
        style={{ backgroundColor: s.background }}
        title={`Background: ${s.background}`}
      />
    </span>
  );
}

export function ThemeSwitcherFab() {
  const { palette, mode, activePalette, palettes, setPalette, setMode } = useTheme();
  const [open, setOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const rootRef = useRef<HTMLDivElement>(null);
  const fabRef = useRef<HTMLButtonElement>(null);
  const menuId = useId();
  const paletteLabelId = useId();
  const paletteValueId = useId();
  const listboxId = useId();

  // Close panel on outside click or Escape key
  useEffect(() => {
    if (!open) return;

    const handlePointerDown = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
        setDropdownOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        if (dropdownOpen) {
          setDropdownOpen(false);
        } else {
          setOpen(false);
          fabRef.current?.focus();
        }
      }
    };

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, dropdownOpen]);

  const handleSelectPalette = (id: PaletteId) => {
    setPalette(id);
    setDropdownOpen(false);
  };

  const handleToggleFab = () => {
    setOpen((prev) => {
      if (prev) setDropdownOpen(false);
      return !prev;
    });
  };

  return (
    <div ref={rootRef} className="theme-fab-root" data-testid="global-theme-switcher">
      {/* Popover Panel (opens strictly ABOVE the FAB) */}
      {open && (
        <div
          id={menuId}
          role="dialog"
          aria-label="Theme and color palette settings"
          className="theme-popover-enter absolute bottom-[calc(100%+0.75rem)] right-0 w-[min(20.5rem,calc(100vw-2rem))] rounded-2xl border border-line bg-panel p-4 text-ink shadow-lg"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-line pb-2.5 mb-3.5">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary-soft text-primary-ink">
                <Palette size={15} />
              </span>
              <div>
                <p className="text-xs font-bold leading-tight text-ink">Appearance</p>
                <p className="text-[11px] leading-tight text-muted">
                  {activePalette.name} · {mode === "dark" ? "Night" : "Light"}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                setDropdownOpen(false);
                fabRef.current?.focus();
              }}
              aria-label="Close theme menu"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-surface hover:text-ink transition"
            >
              <X size={15} />
            </button>
          </div>

          <div className="space-y-4">
            {/* 1. Palette Dropdown */}
            <div className="relative">
              <label
                id={paletteLabelId}
                className="block text-[11px] font-bold uppercase tracking-wider text-muted mb-1.5"
              >
                Color Palette
              </label>

              <button
                type="button"
                aria-labelledby={`${paletteLabelId} ${paletteValueId}`}
                aria-haspopup="listbox"
                aria-expanded={dropdownOpen}
                aria-controls={listboxId}
                onClick={() => setDropdownOpen((v) => !v)}
                className="flex w-full items-center justify-between gap-2 rounded-xl border border-line bg-surface px-3 py-2.5 text-left text-xs font-semibold text-ink hover:border-primary transition"
              >
                <span className="flex items-center gap-2.5 min-w-0">
                  <SwatchPreview definition={activePalette} mode={mode} />
                  <span id={paletteValueId} className="truncate">{activePalette.name}</span>
                </span>
                <ChevronDown
                  size={15}
                  className={`shrink-0 text-muted transition-transform duration-150 ${
                    dropdownOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {dropdownOpen && (
                <ul
                  id={listboxId}
                  role="listbox"
                  aria-labelledby={paletteLabelId}
                  className="mt-1.5 max-h-60 overflow-y-auto rounded-xl border border-line bg-panel p-1.5 shadow-panel space-y-1"
                >
                  {palettes.map((item) => {
                    const isSelected = item.id === palette;
                    return (
                      <li key={item.id} role="option" aria-selected={isSelected}>
                        <button
                          type="button"
                          onClick={() => handleSelectPalette(item.id)}
                          className={`flex w-full items-center justify-between gap-2 rounded-lg px-2.5 py-2 text-left text-xs transition ${
                            isSelected
                              ? "bg-primary-soft text-primary-ink font-bold"
                              : "text-ink hover:bg-surface font-medium"
                          }`}
                        >
                          <div className="flex items-center gap-2.5 min-w-0">
                            <SwatchPreview definition={item} mode={mode} />
                            <div className="min-w-0">
                              <span className="block truncate">{item.name}</span>
                              <span className="block truncate text-[10px] text-muted font-normal">
                                {item.subtitle}
                              </span>
                            </div>
                          </div>
                          {isSelected && (
                            <Check size={14} className="shrink-0 text-primary-ink" />
                          )}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

            {/* 2. Light / Night Mode Segmented Switch */}
            <div>
              <span className="block text-[11px] font-bold uppercase tracking-wider text-muted mb-1.5">
                Mode
              </span>
              <div
                role="radiogroup"
                aria-label="Color mode"
                className="grid grid-cols-2 gap-1 rounded-xl border border-line bg-surface p-1"
              >
                <button
                  type="button"
                  role="radio"
                  aria-checked={mode === "light"}
                  onClick={() => setMode("light")}
                  className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition ${
                    mode === "light"
                      ? "bg-panel text-primary-ink shadow-xs border border-line/60"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  <Sun size={14} />
                  <span>Light</span>
                </button>
                <button
                  type="button"
                  role="radio"
                  aria-checked={mode === "dark"}
                  onClick={() => setMode("dark")}
                  className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition ${
                    mode === "dark"
                      ? "bg-panel text-primary-ink shadow-xs border border-line/60"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  <Moon size={14} />
                  <span>Night</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Single Round Floating Action Button (~56px, bottom-right, site-wide) */}
      <button
        ref={fabRef}
        type="button"
        onClick={handleToggleFab}
        aria-label="Open theme and palette switcher"
        aria-expanded={open}
        aria-controls={menuId}
        aria-haspopup="dialog"
        className="relative flex h-14 w-14 items-center justify-center rounded-full bg-primary text-on-primary shadow-lg border border-line/20 hover:bg-primary-hover hover:scale-105 active:scale-95 transition-transform"
      >
        <Palette size={22} />
        <span
          aria-hidden="true"
          className="pointer-events-none absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full border border-line bg-panel text-primary-ink shadow-xs"
        >
          {mode === "dark" ? <Moon size={11} /> : <Sun size={11} />}
        </span>
      </button>
    </div>
  );
}
