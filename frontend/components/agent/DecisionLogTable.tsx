"use client";

import { useState } from "react";
import useSWR from "swr";
import { Bot, ChevronDown, ChevronUp } from "lucide-react";
import type { DetectionLog } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";
import { EmptyState } from "@/components/shared/EmptyState";

export function DecisionLogTable({ initialLogs }: { initialLogs: DetectionLog[] }) {
  const { data } = useSWR<DetectionLog[]>("/api/agent/log", { fallbackData: initialLogs, refreshInterval: 30000 });
  const [expanded, setExpanded] = useState<string | null>(null);
  const logs = data || initialLogs;

  if (!logs.length) {
    return <EmptyState icon={Bot} title="No decisions logged yet" message="Agent decisions will appear here after the first detection cycle." />;
  }

  return (
    <section className="overflow-hidden rounded-lg border border-hairline bg-canvas shadow-card">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-canvas-soft font-mono text-xs text-body">
          <tr>
            <th className="border-b border-hairline px-4 py-3 font-normal">Logged</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Contract</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Events</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Trace</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => {
            const open = expanded === log.id;
            return (
              <tr key={log.id} className="border-b border-hairline align-top last:border-b-0">
                <td className="px-4 py-4 font-mono text-xs text-body">{new Date(log.logged_at).toLocaleString()}</td>
                <td className="px-4 py-4">{log.contract_address ? <AddressDisplay address={log.contract_address} /> : <span className="text-mute">System</span>}</td>
                <td className="px-4 py-4 text-body">{log.event_ids?.length || 0}</td>
                <td className="px-4 py-4">
                  <button
                    type="button"
                    className="inline-flex h-8 items-center gap-2 rounded-md border border-hairline bg-canvas px-3 text-sm text-ink"
                    onClick={() => setExpanded(open ? null : log.id)}
                  >
                    {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    Prompt / response
                  </button>
                  {open ? (
                    <div className="mt-3 grid gap-3 lg:grid-cols-2">
                      <pre className="max-h-72 overflow-auto rounded-md bg-canvas-soft p-4 font-mono text-xs leading-5 text-body">{log.prompt || "No prompt captured."}</pre>
                      <pre className="max-h-72 overflow-auto rounded-md bg-ink p-4 font-mono text-xs leading-5 text-white">{log.raw_response || "No response captured."}</pre>
                    </div>
                  ) : null}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
