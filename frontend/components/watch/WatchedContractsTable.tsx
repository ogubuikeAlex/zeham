"use client";

import useSWR from "swr";
import { Search } from "lucide-react";
import type { WatchedContract } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";
import { EmptyState } from "@/components/shared/EmptyState";

export function WatchedContractsTable({ initialContracts }: { initialContracts: WatchedContract[] }) {
  const { data, mutate } = useSWR<WatchedContract[]>("/api/contracts", { fallbackData: initialContracts, refreshInterval: 30000 });
  const contracts = data || initialContracts;

  if (!contracts.length) {
    return <EmptyState icon={Search} title="No contracts being watched" message="Add a contract address above to start monitoring." />;
  }

  return (
    <section className="overflow-hidden rounded-lg border border-hairline bg-canvas shadow-card">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-canvas-soft font-mono text-xs text-body">
          <tr>
            <th className="border-b border-hairline px-4 py-3 font-normal">Contract</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Status</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Events</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Added</th>
          </tr>
        </thead>
        <tbody>
          {contracts.map((contract) => (
            <tr key={contract.id || contract.address} className="border-b border-hairline last:border-b-0">
              <td className="px-4 py-4"><AddressDisplay address={contract.address} label={contract.label} /></td>
              <td className="px-4 py-4">
                <span className={`rounded-full px-2 py-1 font-mono text-xs ${contract.active ? "bg-blue-50 text-link" : "bg-canvas-soft text-body"}`}>
                  {contract.active ? "active" : "inactive"}
                </span>
              </td>
              <td className="px-4 py-4 text-body">{contract.event_count?.toLocaleString?.() || 0}</td>
              <td className="px-4 py-4 font-mono text-xs text-body">{contract.added_at ? new Date(contract.added_at).toLocaleDateString() : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="sr-only" onClick={() => mutate()} aria-label="Refresh watchlist" />
    </section>
  );
}
