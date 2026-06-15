import type { Severity } from "@/types";
import { severityClass } from "@/lib/formatters";

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={`inline-flex h-6 items-center rounded-full border px-2 font-mono text-xs ${severityClass(severity)}`}>
      {severity}
    </span>
  );
}
