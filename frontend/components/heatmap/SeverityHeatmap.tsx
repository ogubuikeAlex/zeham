"use client";

import useSWR from "swr";
import { BarChart3 } from "lucide-react";
import type { HeatmapCell, HeatmapResponse, Severity } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";
import { EmptyState } from "@/components/shared/EmptyState";
import { severityRank, truncateMiddle } from "@/lib/formatters";

const hours = Array.from({ length: 24 }, (_, index) => index);

function cellClass(cell?: HeatmapCell) {
  if (!cell || cell.alert_count === 0) return "bg-canvas-soft";
  const tone: Record<Severity, string> = {
    LOW: "bg-blue-100",
    MEDIUM: "bg-amber-200",
    HIGH: "bg-orange-300",
    CRITICAL: "bg-red-500"
  };
  return tone[cell.worst_severity];
}

export function SeverityHeatmap({ initialHeatmap }: { initialHeatmap: HeatmapResponse }) {
  const { data } = useSWR<HeatmapResponse>("/api/heatmap", { fallbackData: initialHeatmap, refreshInterval: 60000 });
  const heatmap = data || initialHeatmap;
  const contracts = Array.from(new Set(heatmap.cells.map((cell) => cell.contract_address))).slice(0, 20);
  const byContractHour = new Map(heatmap.cells.map((cell) => [`${cell.contract_address}:${cell.hour}`, cell]));

  if (!contracts.length) {
    return <EmptyState icon={BarChart3} title="No alert data yet" message="The heatmap will populate as alerts are detected." />;
  }

  return (
    <section className="overflow-x-auto rounded-lg border border-hairline bg-canvas p-4 shadow-card">
      <div className="min-w-[980px]">
        <div className="grid grid-cols-[220px_repeat(24,minmax(28px,1fr))] gap-1">
          <div />
          {hours.map((hour) => (
            <div key={hour} className="text-center font-mono text-xs text-mute">{hour}</div>
          ))}
          {contracts.map((contract) => (
            <Row key={contract} contract={contract} cells={hours.map((hour) => byContractHour.get(`${contract}:${hour}`))} />
          ))}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-3 font-mono text-xs text-body">
        <span>LOW</span><span className="h-3 w-8 rounded-sm bg-blue-100" />
        <span>MEDIUM</span><span className="h-3 w-8 rounded-sm bg-amber-200" />
        <span>HIGH</span><span className="h-3 w-8 rounded-sm bg-orange-300" />
        <span>CRITICAL</span><span className="h-3 w-8 rounded-sm bg-red-500" />
      </div>
    </section>
  );
}

function Row({ contract, cells }: { contract: string; cells: Array<HeatmapCell | undefined> }) {
  const label = cells.find(Boolean)?.contract_label || truncateMiddle(contract);
  return (
    <>
      <div className="flex min-h-8 items-center pr-3">
        <AddressDisplay address={contract} label={label} />
      </div>
      {cells.map((cell, index) => (
        <div
          key={index}
          title={cell ? `${cell.alert_count} alerts, worst ${cell.worst_severity}` : "No alerts"}
          className={`h-8 rounded-sm border border-white ${cellClass(cell)}`}
          style={{ opacity: cell ? Math.min(1, 0.35 + cell.alert_count / 8 + severityRank[cell.worst_severity] / 12) : 1 }}
        />
      ))}
    </>
  );
}
