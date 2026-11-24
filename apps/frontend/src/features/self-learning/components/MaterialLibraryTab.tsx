import React, { useState, useRef } from "react";
import {
  FileText,
  UploadCloud,
  Trash2,
  HardDrive,
  Tag,
  CheckCircle2,
  AlertCircle,
  FileCode,
  FileSpreadsheet,
  Layers,
} from "lucide-react";
import type { SelfLearningMaterial, StorageQuota } from "../types";

interface MaterialLibraryTabProps {
  materials: SelfLearningMaterial[];
  quota: StorageQuota | null;
  onUpload: (file: File, title?: string) => Promise<void>;
  onDeleteMaterial: (materialId: string) => Promise<void>;
  isUploading?: boolean;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export const MaterialLibraryTab: React.FC<MaterialLibraryTabProps> = ({
  materials,
  quota,
  onUpload,
  onDeleteMaterial,
  isUploading = false,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
    if (!docTitle) {
      setDocTitle(file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " "));
    }
    setUploadError(null);
    setUploadSuccess(null);
  };

  const executeUpload = async () => {
    if (!selectedFile) return;
    setUploadError(null);
    setUploadSuccess(null);
    try {
      await onUpload(selectedFile, docTitle.trim() || undefined);
      setUploadSuccess(`Successfully ingested "${selectedFile.name}" with Gemini topics & pgvector chunks.`);
      setSelectedFile(null);
      setDocTitle("");
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Failed to upload document.");
    }
  };

  // Quota bar colors
  const quotaPct = quota ? quota.used_percentage : 0;
  const quotaColor =
    quotaPct > 90
      ? "bg-danger"
      : quotaPct > 75
      ? "bg-warning"
      : "bg-primary";

  return (
    <div className="space-y-6">
      {/* 100MB Storage Quota Meter */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary-ink">
              <HardDrive className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm">Student Document Storage Quota</h3>
              <p className="text-xs text-muted">
                {quota ? formatBytes(quota.used_bytes) : "0 B"} used of 100 MB capacity (
                {quota?.materials_count ?? 0} files)
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-surface border border-line">
            {quotaPct.toFixed(1)}% Used
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mt-4 h-2.5 w-full overflow-hidden rounded-full bg-surface border border-line">
          <div
            className={`h-full transition-all duration-500 ${quotaColor}`}
            style={{ width: `${Math.min(100, Math.max(1, quotaPct))}%` }}
          />
        </div>
      </div>

      {/* Drag & Drop Uploader */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition ${
          dragActive
            ? "border-primary bg-primary-soft/50"
            : "border-line bg-panel hover:border-primary/60"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.pptx,.txt"
          onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0])}
          className="hidden"
          id="file-upload-input"
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary-soft text-primary-ink">
            <UploadCloud className="h-7 w-7" />
          </div>

          <h4 className="font-bold text-base mt-2">
            Drag & Drop educational materials here, or{" "}
            <label
              htmlFor="file-upload-input"
              className="cursor-pointer text-primary-ink hover:underline font-semibold"
            >
              browse files
            </label>
          </h4>
          <p className="text-xs text-muted">
            Supports PDF, Word (.docx), PowerPoint (.pptx), and plain text (.txt). SHA-256 deduplicated.
          </p>
        </div>

        {/* Selected file confirmation */}
        {selectedFile && (
          <div className="mt-6 mx-auto max-w-md rounded-xl border border-line bg-surface p-4 text-left shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 truncate">
                <FileText className="h-5 w-5 text-primary-ink shrink-0" />
                <span className="text-sm font-semibold truncate">{selectedFile.name}</span>
                <span className="text-xs text-muted">({formatBytes(selectedFile.size)})</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="text-muted hover:text-danger-ink text-xs font-semibold"
              >
                Clear
              </button>
            </div>

            <div className="mt-3">
              <label className="block text-xs font-semibold text-muted">Document Title (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Chapter 4: Neural Networks & Backpropagation"
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-line bg-panel p-2 text-sm text-ink"
              />
            </div>

            <button
              type="button"
              disabled={isUploading}
              onClick={executeUpload}
              className="mt-4 w-full rounded-xl bg-primary py-2.5 text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover disabled:opacity-50"
            >
              {isUploading ? "Ingesting & Extracting Gemini RAG Chunks..." : "Upload & Analyze Syllabus"}
            </button>
          </div>
        )}

        {/* Feedback messages */}
        {uploadError && (
          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-danger-ink">
            <AlertCircle className="h-4 w-4" />
            <span>{uploadError}</span>
          </div>
        )}
        {uploadSuccess && (
          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-success-ink">
            <CheckCircle2 className="h-4 w-4" />
            <span>{uploadSuccess}</span>
          </div>
        )}
      </div>

      {/* Document Inventory */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Document Inventory</h3>
          <span className="text-xs text-muted font-semibold">
            {materials.length} uploaded {materials.length === 1 ? "document" : "documents"}
          </span>
        </div>

        {materials.length === 0 ? (
          <div className="rounded-2xl border border-line bg-panel p-8 text-center text-muted">
            <FileCode className="h-8 w-8 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No study documents uploaded for this subject yet.</p>
            <p className="text-xs mt-1">Upload textbooks, slides, or syllabi above to activate Gemini RAG.</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {materials.map((mat) => (
              <div
                key={mat.id}
                className="flex flex-col justify-between rounded-2xl border border-line bg-panel p-5 shadow-xs transition hover:border-primary/50"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface border border-line text-primary-ink">
                        {mat.file_type === "pdf" ? (
                          <FileText className="h-5 w-5" />
                        ) : mat.file_type === "pptx" ? (
                          <Layers className="h-5 w-5" />
                        ) : (
                          <FileSpreadsheet className="h-5 w-5" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-bold text-sm line-clamp-1">{mat.title}</h4>
                        <p className="text-xs text-muted mt-0.5">
                          {mat.file_name} • {formatBytes(mat.file_size_bytes)} • {mat.chunks_count} pgvector chunks
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => onDeleteMaterial(mat.id)}
                      title="Delete document"
                      className="rounded-lg p-1.5 text-muted hover:bg-danger-soft hover:text-danger-ink transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Extracted Gemini Topics */}
                  {mat.extracted_topics && mat.extracted_topics.length > 0 && (
                    <div className="mt-4">
                      <p className="flex items-center gap-1.5 text-xs font-semibold text-muted mb-2">
                        <Tag className="h-3.5 w-3.5 text-primary-ink" />
                        <span>Gemini Syllabus Topics ({mat.extracted_topics.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {mat.extracted_topics.map((t, i) => (
                          <span
                            key={i}
                            className="inline-flex items-center rounded-md bg-surface px-2 py-1 text-xs font-medium text-ink border border-line"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-between pt-3 border-t border-line text-xs text-muted">
                  <span>SHA-256: {mat.file_hash.slice(0, 12)}...</span>
                  <time>{new Date(mat.created_at).toLocaleDateString()}</time>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
