"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { Alert } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";
import { RelativeTime } from "@/components/shared/RelativeTime";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { TxHashLink } from "@/components/shared/TxHashLink";
import { confidenceLabel } from "@/lib/formatters";

export function AlertCard({ alert }: { alert: Alert }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <article className="rounded-lg border border-hairline bg-canvas p-5 shadow-card">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={alert.severity} />
            <span className="rounded-full bg-canvas-soft px-2 py-1 font-mono text-xs text-body">{alert.source}</span>
            <span className="font-mono text-xs text-mute">
              <RelativeTime value={alert.fired_at} />
            </span>
          </div>
          <h2 className="mt-3 text-xl font-semibold tracking-[-0.4px] text-ink">{alert.anomaly_type}</h2>
          <p className="mt-2 text-sm leading-6 text-body">{alert.reason}</p>
        </div>
        <button
          type="button"
          title={expanded ? "Collapse alert" : "Expand alert"}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-hairline bg-canvas text-body hover:text-ink"
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>
      <div className="mt-4 grid gap-3 border-t border-hairline pt-4 text-sm md:grid-cols-2 xl:grid-cols-4">
        <div>
          <p className="font-mono text-xs text-mute">Contract</p>
          <div className="mt-1"><AddressDisplay address={alert.contract_address} /></div>
        </div>
        <div>
          <p className="font-mono text-xs text-mute">Confidence</p>
          <p className="mt-1 text-ink">{confidenceLabel(alert.confidence)}</p>
        </div>
        <div>
          <p className="font-mono text-xs text-mute">Decision record</p>
          <div className="mt-1"><TxHashLink tx={alert.on_chain_tx} /></div>
        </div>
        <div>
          <p className="font-mono text-xs text-mute">Fired at</p>
          <p className="mt-1 font-mono text-xs text-body">{new Date(alert.fired_at).toLocaleString()}</p>
        </div>
      </div>
      {expanded && alert.recommended_action ? (
        <div className="mt-4 rounded-md bg-canvas-soft p-4 text-sm text-body">
          <span className="font-medium text-ink">Recommended action: </span>
          {alert.recommended_action}
        </div>
      ) : null}
    </article>
  );
}
