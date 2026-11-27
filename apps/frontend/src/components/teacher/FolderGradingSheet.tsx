import { useEffect, useState } from "react";
import { Check, Edit3, FileText, X } from "lucide-react";
import type {
  ClassAssessmentFolder,
  FacultyClassInfo,
  FolderAssessmentMarkRow
} from "../../features/teacher/teacher-portal-data";

interface Props {
  folder: ClassAssessmentFolder;
  classInfo?: FacultyClassInfo;
  onSaveFolder: (updated: ClassAssessmentFolder) => void;
  onClose?: () => void;
}

/** Student submissions & marks entry sheet for an Assignment 1, Assignment 2, or Quizzes folder. */
export function FolderGradingSheet({ folder, classInfo, onSaveFolder, onClose }: Props) {
  const [rows, setRows] = useState<FolderAssessmentMarkRow[]>(folder.rows);
  const [notice, setNotice] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(true);

  useEffect(() => {
    setRows(folder.rows);
    setNotice(null);
    setIsEditing(true);
    // Only reset local draft state when switching to a different folder ID.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [folder.id]);

  const gradedCount = rows.filter((r) => r.marks !== null).length;
  const pendingCount = rows.length - gradedCount;

  const updateStudentMark = (studentId: string, rawValue: string) => {
    const trimmed = rawValue.trim();
    if (!trimmed) {
      setRows((prev) =>
        prev.map((r) => (r.studentId === studentId ? { ...r, marks: null } : r))
      );
      return;
    }
    const parsed = Number(trimmed);
    if (Number.isNaN(parsed)) return;
    const clamped = Math.min(folder.maxMarks, Math.max(0, parsed));
    setRows((prev) =>
      prev.map((r) => (r.studentId === studentId ? { ...r, marks: clamped } : r))
    );
  };

  const handleSave = () => {
    const updated: ClassAssessmentFolder = { ...folder, rows };
    onSaveFolder(updated);
    setIsEditing(false);
    setNotice(`Saved marks for ${gradedCount} of ${rows.length} students in ${folder.folderName}.`);
  };

  return (
    <div className="rounded-2xl border border-line bg-panel p-4 sm:p-5 space-y-4 shadow-xs">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            {classInfo && (
              <span className="font-mono text-xs font-bold text-primary-ink">
                {classInfo.courseCode} · {classInfo.section}
              </span>
            )}
            <span className="rounded-md bg-primary-soft px-2 py-0.5 text-xs font-bold text-primary-ink">
              {folder.folderName}
            </span>
            <span
              className={`rounded-md px-2 py-0.5 text-xs font-bold ${
                pendingCount === 0
                  ? "bg-success-soft text-success-ink"
                  : "bg-warning-soft text-warning-ink"
              }`}
            >
              {pendingCount === 0 ? "All Graded" : `${pendingCount} to Grade`}
            </span>
          </div>
          <h3 className="mt-1 text-base font-bold text-ink">{folder.subtitle}</h3>
          <p className="text-xs text-muted mt-0.5">
            Total Marks: {folder.maxMarks} · {gradedCount} / {rows.length} evaluated
          </p>
        </div>

        <div className="flex items-center gap-2">
          {!isEditing && (
            <button
              type="button"
              onClick={() => {
                setIsEditing(true);
                setNotice(null);
              }}
              className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer"
            >
              <Edit3 size={14} />
              <span>Edit Marks</span>
            </button>
          )}
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              aria-label="Close grading sheet"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-line bg-surface text-muted hover:text-ink transition cursor-pointer"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {notice && (
        <div
          role="status"
          className="rounded-xl border border-success/40 bg-success-soft px-3.5 py-2.5 text-xs font-semibold text-success-ink"
        >
          {notice}
        </div>
      )}

      <div className="overflow-x-auto rounded-2xl border border-line">
        <table className="w-full text-left text-xs sm:text-sm">
          <thead className="bg-surface text-[11px] font-bold uppercase tracking-wider text-muted">
            <tr>
              <th className="px-3 py-2.5">Roll No</th>
              <th className="px-3 py-2.5">Student Name</th>
              <th className="px-3 py-2.5">Submission</th>
              <th className="px-3 py-2.5 text-right">Marks / {folder.maxMarks}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line bg-panel">
            {rows.map((row) => (
              <tr key={row.studentId}>
                <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs font-bold text-primary-ink">
                  {row.rollNo}
                </td>
                <td className="px-3 py-2.5 font-semibold text-ink">{row.studentName}</td>
                <td className="px-3 py-2.5">
                  <span className="inline-flex items-center gap-1.5 text-xs text-muted">
                    <FileText size={13} className="shrink-0 text-primary-ink" />
                    <span className="truncate max-w-[170px] sm:max-w-xs">{row.submittedFile}</span>
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right">
                  <input
                    type="number"
                    min={0}
                    max={folder.maxMarks}
                    step={0.5}
                    disabled={!isEditing}
                    aria-label={`Marks for ${row.studentName}`}
                    placeholder="—"
                    value={row.marks ?? ""}
                    onChange={(e) => updateStudentMark(row.studentId, e.target.value)}
                    className="w-20 min-h-10 rounded-xl border border-line bg-surface px-2.5 py-1.5 text-right text-sm sm:text-xs font-bold text-ink focus:outline-hidden focus:ring-2 focus:ring-primary disabled:opacity-75"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-end gap-2 pt-1">
        {isEditing ? (
          <button
            type="button"
            onClick={handleSave}
            className="inline-flex min-h-11 items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-on-primary shadow-xs hover:bg-primary-hover transition cursor-pointer"
          >
            <Check size={15} />
            <span>Save Marks</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              setIsEditing(true);
              setNotice(null);
            }}
            className="inline-flex min-h-11 items-center gap-1.5 rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer"
          >
            <Edit3 size={14} />
            <span>Edit Marks</span>
          </button>
        )}
      </div>
    </div>
  );
}
