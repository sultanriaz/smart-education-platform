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

/**
 * Renders prose mixed with inline `$...$` or block `$$...$$` LaTeX segments.
 */
export const RichMathText: React.FC<{ text: string; className?: string }> = ({
  text,
  className = "",
}) => {
  const parts = useMemo(() => {
    if (!text) return [];
    // Split on $$...$$ or $...$
    return text.split(/(\$\$[^$]+\$\$|\$[^$\n]+\$)/g);
  }, [text]);

  return (
    <span className={className}>
      {parts.map((part, idx) => {
        if (part.startsWith("$$") && part.endsWith("$$")) {
          const expr = part.slice(2, -2).trim();
          try {
            const html = katex.renderToString(expr, { displayMode: true, throwOnError: false });
            return <span key={idx} className="block my-1.5 overflow-x-auto" dangerouslySetInnerHTML={{ __html: html }} />;
          } catch {
            return <span key={idx}>{part}</span>;
          }
        }
        if (part.startsWith("$") && part.endsWith("$") && part.length > 2) {
          const expr = part.slice(1, -1).trim();
          try {
            const html = katex.renderToString(expr, { displayMode: false, throwOnError: false });
            return <span key={idx} dangerouslySetInnerHTML={{ __html: html }} />;
          } catch {
            return <span key={idx}>{part}</span>;
          }
        }
        return <React.Fragment key={idx}>{part}</React.Fragment>;
      })}
    </span>
  );
};
