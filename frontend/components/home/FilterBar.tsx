"use client";

import type { Severity } from "@/types";

const severities: Array<"ALL" | Severity> = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

export function FilterBar({
  severity,
  type,
  types,
  onSeverity,
  onType
}: {
  severity: "ALL" | Severity;
  type: string;
  types: string[];
  onSeverity: (severity: "ALL" | Severity) => void;
  onType: (type: string) => void;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-hairline bg-canvas p-3 shadow-card lg:flex-row lg:items-center lg:justify-between">
      <div className="flex gap-1 overflow-x-auto">
        {severities.map((item) => (
          <button
            key={item}
            type="button"
            className={`h-8 rounded-full px-3 text-sm ${severity === item ? "bg-ink text-white" : "bg-canvas-soft text-body hover:text-ink"}`}
            onClick={() => onSeverity(item)}
          >
            {item}
          </button>
        ))}
      </div>
      <select
        value={type}
        onChange={(event) => onType(event.target.value)}
        className="h-9 rounded-md border border-hairline bg-canvas px-3 text-sm text-ink"
      >
        <option value="ALL">All anomaly types</option>
        {types.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </div>
  );
}
