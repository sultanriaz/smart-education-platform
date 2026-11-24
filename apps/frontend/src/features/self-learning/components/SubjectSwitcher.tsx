import React, { useState } from "react";
import { BookOpen, ChevronDown, Plus, Sparkles, X } from "lucide-react";
import { useTheme } from "../../../theme/themeContextState";
import type { SelfLearningSubject, SubjectCreatePayload } from "../types";

interface SubjectSwitcherProps {
  subjects: SelfLearningSubject[];
  activeSubject: SelfLearningSubject | null;
  onSelectSubject: (subject: SelfLearningSubject) => void;
  onCreateSubject: (payload: SubjectCreatePayload) => Promise<void>;
  isLoading?: boolean;
}

const DEPARTMENTS = [
  "Computer Science",
  "Software Engineering",
  "Faculty of Law",
  "Health Sciences & Medicine",
  "Physics & Mathematics",
  "Business & Economics",
  "Humanities & Social Sciences",
  "General",
];

type ColorSlotKey = "primary" | "secondary" | "accent" | "success" | "warning";

const PRESET_TOKEN_SLOTS: { key: ColorSlotKey; label: string; cssVar: string; dotClass: string }[] = [
  { key: "primary", label: "Primary", cssVar: "--primary", dotClass: "bg-primary" },
  { key: "secondary", label: "Secondary", cssVar: "--secondary", dotClass: "bg-secondary" },
  { key: "accent", label: "Accent", cssVar: "--accent", dotClass: "bg-accent" },
  { key: "success", label: "Success", cssVar: "--success", dotClass: "bg-success" },
  { key: "warning", label: "Highlight", cssVar: "--warning", dotClass: "bg-warning" },
];

export const SubjectSwitcher: React.FC<SubjectSwitcherProps> = ({
  subjects,
  activeSubject,
  onSelectSubject,
  onCreateSubject,
  isLoading = false,
}) => {
  const { activePalette, mode } = useTheme();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("Computer Science");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [colorSlot, setColorSlot] = useState<ColorSlotKey>("primary");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Subject name is required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const modeTokens = activePalette.modes[mode];
      const resolvedHex = modeTokens[colorSlot] ?? modeTokens.primary;
      await onCreateSubject({
        name: name.trim(),
        department,
        code: code.trim() || undefined,
        description: description.trim() || undefined,
        color_hex: resolvedHex,
      });
      setName("");
      setCode("");
      setDescription("");
      setModalOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create subject.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-line bg-panel p-4 shadow-xs">
        {/* Active Subject Selector */}
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-on-primary shadow-xs">
            <BookOpen className="h-6 w-6" />
          </div>

          <div className="relative">
            <button
              type="button"
              onClick={() => setDropdownOpen((v) => !v)}
              className="flex items-center gap-2 text-left font-bold text-lg hover:opacity-80 transition"
              aria-haspopup="listbox"
              aria-expanded={dropdownOpen}
            >
              <span>{activeSubject ? activeSubject.name : "Select a Subject..."}</span>
              <ChevronDown className="h-4 w-4 text-muted" />
            </button>
            <div className="flex items-center gap-2 text-xs text-muted">
              {activeSubject?.code ? (
                <span className="font-mono bg-surface px-1.5 py-0.5 rounded border border-line">
                  {activeSubject.code}
                </span>
              ) : null}
              <span>{activeSubject?.department || "Personal Subject Workspace"}</span>
              {activeSubject ? (
                <span>• {activeSubject.materials_count} materials</span>
              ) : null}
            </div>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <div className="absolute left-0 top-full z-30 mt-2 w-72 rounded-xl border border-line bg-panel p-2 shadow-xl">
                <div className="max-h-60 overflow-y-auto space-y-1">
                  {subjects.map((sub, idx) => (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => {
                        onSelectSubject(sub);
                        setDropdownOpen(false);
                      }}
                      className={`flex w-full items-center justify-between rounded-lg p-2.5 text-left text-sm transition ${
                        sub.id === activeSubject?.id
                          ? "bg-primary-soft text-primary-ink font-semibold"
                          : "hover:bg-surface"
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span
                          className={`h-2.5 w-2.5 shrink-0 rounded-full ${
                            idx % 3 === 0 ? "bg-primary" : idx % 3 === 1 ? "bg-secondary" : "bg-accent"
                          }`}
                        />
                        <span className="truncate">{sub.name}</span>
                      </div>
                      <span className="text-xs text-muted shrink-0 ml-2">
                        {sub.materials_count} docs
                      </span>
                    </button>
                  ))}
                  {subjects.length === 0 && (
                    <p className="p-3 text-center text-xs text-muted">No custom subjects yet.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Button: + Add Subject */}
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
        >
          <Plus className="h-4 w-4" />
          <span>Add Subject</span>
        </button>
      </div>

      {/* Add Subject Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl border border-line bg-panel p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-line">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary-ink" />
                <h3 className="text-lg font-bold">Create Dynamic Subject</h3>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="rounded-lg p-1 text-muted hover:bg-surface"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              {error && (
                <div className="rounded-xl bg-danger-soft p-3 text-sm text-danger-ink border border-danger/40">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-muted uppercase">Subject Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Advanced Deep Learning & Transformers"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-line bg-surface p-2.5 text-sm text-ink"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase">Course Code</label>
                  <input
                    type="text"
                    placeholder="e.g. CS-501"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-line bg-surface p-2.5 text-sm text-ink"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase">Department</label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-line bg-surface p-2.5 text-sm text-ink"
                  >
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted uppercase">Description</label>
                <textarea
                  rows={2}
                  placeholder="Goals, target competencies, and curriculum focus..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-line bg-surface p-2.5 text-sm text-ink"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted uppercase">Subject Accent Token</label>
                <div className="mt-2 flex items-center gap-2.5">
                  {PRESET_TOKEN_SLOTS.map((slot) => (
                    <button
                      key={slot.key}
                      type="button"
                      aria-label={`Select ${slot.label} swatch`}
                      onClick={() => setColorSlot(slot.key)}
                      className={`h-7 w-7 rounded-full border border-line/50 transition ${slot.dotClass} ${
                        colorSlot === slot.key ? "ring-2 ring-offset-2 ring-primary scale-110" : ""
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-line">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="rounded-xl border border-line px-4 py-2 text-sm font-semibold hover:bg-surface"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || isLoading}
                  className="rounded-xl bg-primary px-5 py-2 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover disabled:opacity-50"
                >
                  {submitting ? "Creating..." : "Create Subject"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
