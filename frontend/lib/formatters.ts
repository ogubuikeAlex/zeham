import type { Severity } from "@/types";

export const EXPLORER_BASE = process.env.NEXT_PUBLIC_EXPLORER_BASE || "https://explorer.sepolia.mantle.xyz";

export function truncateMiddle(value: string | null | undefined, start = 6, end = 4) {
  if (!value) return "-";
  if (value.length <= start + end + 3) return value;
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

export function explorerAddressUrl(address: string) {
  return `${EXPLORER_BASE.replace(/\/$/, "")}/address/${address}`;
}

export function explorerTxUrl(tx: string) {
  return `${EXPLORER_BASE.replace(/\/$/, "")}/tx/${tx}`;
}

export function confidenceLabel(confidence: number | null | undefined) {
  if (confidence == null || Number.isNaN(confidence)) return "-";
  const normalized = confidence <= 1 ? confidence * 100 : confidence;
  return `${Math.round(normalized)}%`;
}

export function relativeTime(value: string) {
  const diff = Date.now() - new Date(value).getTime();
  const seconds = Math.max(1, Math.floor(diff / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export const severityRank: Record<Severity, number> = { LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };

export function severityClass(severity: Severity) {
  return {
    CRITICAL: "border-error bg-red-50 text-error",
    HIGH: "border-orange-300 bg-orange-50 text-orange-700",
    MEDIUM: "border-warning bg-amber-50 text-warning-deep",
    LOW: "border-blue-200 bg-blue-50 text-link"
  }[severity];
}
