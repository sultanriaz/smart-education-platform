import React, { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

interface KaTeXViewerProps {
  math: string;
  displayMode?: boolean;
  className?: string;
}

export const KaTeXViewer: React.FC<KaTeXViewerProps> = ({
  math,
  displayMode = true,
  className = "",
}) => {
  const html = useMemo(() => {
    if (!math || !math.trim()) return "";
    // Clean potential markdown delimiters
    const cleanMath = math.replace(/^\$\$|\$\$$|^\\\[|\\\]$/g, "").trim();
    try {
      return katex.renderToString(cleanMath, {
        displayMode,
        throwOnError: false,
      });
    } catch {
      return cleanMath;
    }
  }, [math, displayMode]);

  if (!html) return null;

  return (
    <div
      className={`katex-rendered overflow-x-auto py-1 ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
