import React, { useState } from "react";
import type { TopicMasteryDetail } from "../types";

interface TopicMasteryRadarChartProps {
  topics: TopicMasteryDetail[];
  onSelectTopic?: (topic: string) => void;
}

export const TopicMasteryRadarChart: React.FC<TopicMasteryRadarChartProps> = ({
  topics,
  onSelectTopic,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Limit radar spokes to max 8 cleanest topics for legibility
  const displayTopics = topics.slice(0, 8);
  const count = displayTopics.length;

  if (count === 0) {
    return null;
  }

  // Ensure at least 3 axes for polygon geometry (pad visual axes if < 3)
  const paddedTopics: (TopicMasteryDetail & { isPlaceholder?: boolean })[] = [...displayTopics];
  while (paddedTopics.length < 3) {
    paddedTopics.push({
      topic: `Syllabus Area ${paddedTopics.length + 1}`,
      total_attempted: 0,
      total_correct: 0,
      mastery_percentage: 0,
      status: "Weak",
      recommendation: "Complete more assessments to unlock this axis.",
      isPlaceholder: true,
    });
  }

  const N = paddedTopics.length;
  const size = 340;
  const cx = size / 2;
  const cy = size / 2;
  const radius = 112;
  const rings = [25, 50, 75, 100];

  const getPoint = (index: number, pct: number, rScale = 1) => {
    const angle = (Math.PI * 2 * index) / N - Math.PI / 2;
    const r = (Math.max(4, Math.min(100, pct)) / 100) * radius * rScale;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  const ringPolygon = (pct: number) =>
    Array.from({ length: N })
      .map((_, i) => {
        const pt = getPoint(i, pct);
        return `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
      })
      .join(" ");

  const dataPolygon = paddedTopics
    .map((t, i) => {
      const pt = getPoint(i, t.mastery_percentage);
      return `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
    })
    .join(" ");

  const hoveredTopic = hoveredIdx !== null ? paddedTopics[hoveredIdx] : null;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-full max-w-[360px]">
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="w-full h-auto overflow-visible select-none"
          role="img"
          aria-label="Syllabus topic mastery radar chart"
        >
          {/* Proficiency Zone Concentric Rings */}
          {rings.map((ring) => (
            <polygon
              key={ring}
              points={ringPolygon(ring)}
              fill={
                ring === 100
                  ? "rgba(16, 185, 129, 0.04)"
                  : ring === 75
                  ? "rgba(16, 185, 129, 0.06)"
                  : ring === 50
                  ? "rgba(245, 158, 11, 0.07)"
                  : "rgba(239, 68, 68, 0.07)"
              }
              stroke={
                ring === 75
                  ? "rgba(16, 185, 129, 0.45)"
                  : ring === 50
                  ? "rgba(245, 158, 11, 0.45)"
                  : "currentColor"
              }
              strokeOpacity={ring === 75 || ring === 50 ? 0.8 : 0.16}
              strokeDasharray={ring === 75 || ring === 50 ? "4 3" : undefined}
              strokeWidth={ring === 75 || ring === 50 ? 1.25 : 1}
              className="text-muted"
            />
          ))}

          {/* Ring Percentage Labels along vertical top axis */}
          {[50, 75, 100].map((ring) => {
            const pt = getPoint(0, ring);
            return (
              <text
                key={`lbl-${ring}`}
                x={pt.x + 6}
                y={pt.y + 3}
                fontSize="9"
                className="fill-muted font-mono font-semibold"
              >
                {ring}%
              </text>
            );
          })}

          {/* Axis Spokes & Topic Labels */}
          {paddedTopics.map((item, i) => {
            const outer = getPoint(i, 100);
            const labelPt = getPoint(i, 100, 1.24);
            const anchor =
              Math.abs(labelPt.x - cx) < 12
                ? "middle"
                : labelPt.x > cx
                ? "start"
                : "end";

            const shortLabel =
              item.topic.length > 18 ? `${item.topic.slice(0, 17)}…` : item.topic;

            return (
              <g key={`axis-${i}`}>
                <line
                  x1={cx}
                  y1={cy}
                  x2={outer.x}
                  y2={outer.y}
                  stroke="currentColor"
                  strokeOpacity={0.18}
                  strokeWidth={1}
                  className="text-muted"
                />
                <text
                  x={labelPt.x}
                  y={labelPt.y}
                  textAnchor={anchor}
                  dominantBaseline="middle"
                  fontSize="10"
                  className={`font-semibold transition ${
                    item.isPlaceholder
                      ? "fill-muted/50"
                      : hoveredIdx === i
                      ? "fill-brand-600 font-bold cursor-pointer"
                      : "fill-current text-ink cursor-pointer"
                  }`}
                  onMouseEnter={() => !item.isPlaceholder && setHoveredIdx(i)}
                  onMouseLeave={() => setHoveredIdx(null)}
                  onClick={() => !item.isPlaceholder && onSelectTopic?.(item.topic)}
                >
                  {shortLabel}
                </text>
              </g>
            );
          })}

          {/* Student Mastery Area Polygon */}
          <polygon
            points={dataPolygon}
            fill="rgba(79, 70, 229, 0.22)"
            stroke="#4f46e5"
            strokeWidth={2.5}
            strokeLinejoin="round"
            className="transition-all duration-500"
          />

          {/* Interactive Data Vertices */}
          {paddedTopics.map((item, i) => {
            if (item.isPlaceholder) return null;
            const pt = getPoint(i, item.mastery_percentage);
            const dotColor =
              item.status === "Strong"
                ? "#10b981"
                : item.status === "Moderate"
                ? "#f59e0b"
                : "#ef4444";

            return (
              <g
                key={`dot-${i}`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={() => onSelectTopic?.(item.topic)}
              >
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={hoveredIdx === i ? 7 : 5}
                  fill={dotColor}
                  stroke="white"
                  strokeWidth={2}
                  className="transition-all duration-150"
                />
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend & Active Hover Readout */}
      <div className="mt-2 w-full space-y-2">
        <div className="flex flex-wrap items-center justify-center gap-3 text-[11px] text-muted">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
            Strong (≥75%)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
            Moderate (50–74%)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
            Weak (&lt;50%)
          </span>
        </div>

        <div className="rounded-xl border border-line bg-surface px-3.5 py-2.5 text-center text-xs min-h-[46px] flex items-center justify-center">
          {hoveredTopic && !hoveredTopic.isPlaceholder ? (
            <div className="flex flex-wrap items-center justify-center gap-2">
              <strong className="text-ink">{hoveredTopic.topic}:</strong>
              <span className="font-mono font-bold text-brand-600">
                {hoveredTopic.mastery_percentage}%
              </span>
              <span className="text-muted">
                ({hoveredTopic.total_correct}/{hoveredTopic.total_attempted} correct · {hoveredTopic.status})
              </span>
            </div>
          ) : (
            <span className="text-muted">
              Hover any spoke for topic precision or click a vertex to launch a targeted gap drill.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
