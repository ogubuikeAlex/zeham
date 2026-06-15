"use client";

import type { ConnectionState } from "@/types";

const labels: Record<ConnectionState, string> = {
  connected: "WS connected",
  connecting: "WS connecting",
  reconnecting: "WS reconnecting",
  disconnected: "WS disconnected"
};

const dots: Record<ConnectionState, string> = {
  connected: "bg-blue-500",
  connecting: "bg-warning",
  reconnecting: "bg-warning",
  disconnected: "bg-error"
};

export function ConnectionIndicator({ state = "connecting" }: { state?: ConnectionState }) {
  return (
    <span className="inline-flex h-8 items-center gap-2 rounded-md border border-hairline bg-canvas px-3 font-mono text-xs text-body">
      <span className={`h-2 w-2 rounded-full ${dots[state]}`} />
      {labels[state]}
    </span>
  );
}
