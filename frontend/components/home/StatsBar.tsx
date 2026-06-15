"use client";

import useSWR from "swr";
import type { AlertStats } from "@/types";

const cards = [
  ["total_alerts_today", "Alerts today"],
  ["critical_today", "Critical today"],
  ["contracts_monitored", "Contracts monitored"],
  ["on_chain_decisions", "On-chain decisions"]
] as const;

export function StatsBar({ initialStats }: { initialStats: AlertStats }) {
  const { data } = useSWR<AlertStats>("/api/alerts/stats", { fallbackData: initialStats, refreshInterval: 30000 });
  const stats = data || initialStats;

  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(([key, label]) => (
        <div key={key} className="rounded-lg border border-hairline bg-canvas p-5 shadow-card">
          <p className="font-mono text-xs text-body">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-[-0.8px] text-ink">{stats[key].toLocaleString()}</p>
        </div>
      ))}
    </section>
  );
}
