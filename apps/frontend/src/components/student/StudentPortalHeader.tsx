import { useEffect, useId, useRef, useState, type ChangeEvent } from "react";
import { ArrowLeft, Camera, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth";

export const STUDENT_PHOTO_STORAGE_KEY = "smartedu_student_photo";
const MAX_PHOTO_BYTES = 2 * 1024 * 1024;
const AVATAR_MAX_DIMENSION = 256;

async function optimizeProfilePhotoDataUrl(
  file: File,
  rawDataUrl: string
): Promise<string> {
  if (typeof document === "undefined" || file.type === "image/svg+xml") {
    return rawDataUrl;
  }

  return await new Promise<string>((resolve) => {
    const img = new Image();
    img.onload = () => {
      try {
        const naturalW = img.naturalWidth || img.width;
        const naturalH = img.naturalHeight || img.height;
        if (!naturalW || !naturalH) {
          resolve(rawDataUrl);
          return;
        }
        const scale = Math.min(1, AVATAR_MAX_DIMENSION / Math.max(naturalW, naturalH));
        const targetW = Math.max(1, Math.round(naturalW * scale));
        const targetH = Math.max(1, Math.round(naturalH * scale));
        const canvas = document.createElement("canvas");
        canvas.width = targetW;
        canvas.height = targetH;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          resolve(rawDataUrl);
          return;
        }
        ctx.drawImage(img, 0, 0, targetW, targetH);
        const webpUrl = canvas.toDataURL("image/webp", 0.84);
        if (webpUrl.startsWith("data:image/webp") && webpUrl.length < rawDataUrl.length) {
          resolve(webpUrl);
          return;
        }
        const jpegUrl = canvas.toDataURL("image/jpeg", 0.84);
        resolve(jpegUrl.length < rawDataUrl.length ? jpegUrl : rawDataUrl);
      } catch {
        resolve(rawDataUrl);
      }
    };
    img.onerror = () => resolve(rawDataUrl);
    img.src = rawDataUrl;
  });
}

function formatStudentRegistration(email?: string): string {
  if (!email) {
    return "CIIT/SP23-BCS-155/SWL";
  }

  const normalized = email.trim().toUpperCase();
  if (normalized.startsWith("CIIT/")) {
    return normalized;
  }

  const localPart = normalized.split("@")[0]?.trim() ?? "";
  if (/^[A-Z]{2,6}-\d{2,4}$/.test(localPart)) {
    return `CIIT/SP23-${localPart}/SWL`;
  }

  return "CIIT/SP23-BCS-155/SWL";
}

function readStoredPhoto(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(STUDENT_PHOTO_STORAGE_KEY);
  } catch {
    return null;
  }
}

export interface StudentPortalHeaderProps {
  /** Optional route to navigate back to (rendered as circular back icon button). */
  backTo?: string;
  /** Accessible label for the back button when `backTo` is provided. */
  backLabel?: string;
}

/**
 * Shared curved header for student portal screens showing student ID, Active badge,
 * university subtitle, and persistent local Profile Photo upload/preview control.
 */
export function StudentPortalHeader({
  backTo,
  backLabel = "Go back",
}: StudentPortalHeaderProps) {
  const { user } = useAuth();
  const inputId = useId();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(() => readStoredPhoto());
  const [photoError, setPhotoError] = useState<string | null>(null);

  useEffect(() => {
    setPhotoUrl(readStoredPhoto());
  }, []);

  const registrationId = formatStudentRegistration(user?.email);

  function handleTriggerUpload() {
    setPhotoError(null);
    fileInputRef.current?.click();
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      setPhotoError("Please select an image file.");
      return;
    }

    if (file.size > MAX_PHOTO_BYTES) {
      setPhotoError("Image must be under 2 MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = typeof reader.result === "string" ? reader.result : null;
      if (!result) {
        setPhotoError("Could not load selected image.");
        return;
      }
      void optimizeProfilePhotoDataUrl(file, result).then((optimizedUrl) => {
        setPhotoUrl(optimizedUrl);
        setPhotoError(null);
        try {
          window.localStorage.setItem(STUDENT_PHOTO_STORAGE_KEY, optimizedUrl);
        } catch {
          setPhotoError("Photo preview updated, but browser storage is full.");
        }
      });
    };
    reader.onerror = () => {
      setPhotoError("Could not read selected image.");
    };
    reader.readAsDataURL(file);
  }

  function handleClearPhoto() {
    setPhotoUrl(null);
    setPhotoError(null);
    try {
      window.localStorage.removeItem(STUDENT_PHOTO_STORAGE_KEY);
    } catch {
      // Ignore storage removal errors in restricted browsing contexts.
    }
  }

  return (
    <header className="relative overflow-hidden rounded-b-[1.75rem] bg-gradient-to-br from-hero-bg via-primary to-hero-bg px-5 py-6 text-hero-fg shadow-lg sm:rounded-[1.75rem] sm:px-7 sm:py-6">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-12 -top-14 h-44 w-44 rounded-full bg-hero-fg/10"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-8 -bottom-16 h-36 w-36 rounded-full bg-hero-fg/10"
      />

      <div className="relative flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1 space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            {backTo && (
              <Link
                to={backTo}
                aria-label={backLabel}
                className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-hero-fg/15 text-hero-fg transition hover:bg-hero-fg/25"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
            )}

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-hero-fg/15 px-2.5 py-0.5 text-[11px] font-semibold text-hero-fg">
                  <span className="h-1.5 w-1.5 rounded-full bg-success" aria-hidden="true" />
                  Active
                </span>
              </div>
              <h1 className="mt-1.5 break-words text-[13px] font-bold leading-snug tracking-tight text-hero-fg sm:text-xl">
                Welcome: {registrationId}
              </h1>
              <p className="mt-0.5 text-xs font-medium text-hero-muted sm:text-sm">
                COMSATS University Islamabad
              </p>
            </div>
          </div>

          {photoError && (
            <p role="alert" className="text-xs font-medium text-hero-fg/90">
              {photoError}
            </p>
          )}
        </div>

        <div className="relative shrink-0">
          <input
            ref={fileInputRef}
            id={inputId}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="sr-only"
            aria-label="Upload student profile photo"
          />

          <button
            type="button"
            onClick={handleTriggerUpload}
            aria-label={photoUrl ? "Change Profile Photo" : "Upload Profile Photo"}
            className="group relative flex h-16 w-16 flex-col items-center justify-center overflow-hidden rounded-2xl border border-hero-fg/30 bg-hero-fg/15 text-hero-fg shadow-sm transition hover:bg-hero-fg/25 sm:h-22 sm:w-22"
          >
            {photoUrl ? (
              <>
                <img
                  src={photoUrl}
                  alt="Student profile photo"
                  width={88}
                  height={88}
                  decoding="async"
                  fetchPriority="high"
                  className="aspect-square h-full w-full object-cover"
                />
                <span className="absolute inset-x-0 bottom-0 bg-hero-bg/75 py-0.5 text-center text-[10px] font-semibold text-hero-fg opacity-0 transition group-hover:opacity-100 group-focus-visible:opacity-100">
                  Change
                </span>
              </>
            ) : (
              <span className="flex flex-col items-center justify-center gap-1 px-1.5 text-center">
                <Camera className="h-5 w-5 text-hero-fg/90" aria-hidden="true" />
                <span className="text-[11px] font-semibold leading-tight text-hero-fg">
                  Profile Photo
                </span>
              </span>
            )}
          </button>

          {photoUrl && (
            <button
              type="button"
              onClick={handleClearPhoto}
              aria-label="Remove profile photo"
              title="Remove profile photo"
              className="absolute -right-1.5 -top-1.5 inline-flex h-6 w-6 items-center justify-center rounded-full border border-hero-fg/30 bg-hero-bg text-hero-fg shadow-sm transition hover:bg-danger hover:text-danger-fg"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
