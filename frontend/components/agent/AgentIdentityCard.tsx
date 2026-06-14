"use client";

import useSWR from "swr";
import { BadgeCheck } from "lucide-react";
import type { AgentIdentity } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";

export function AgentIdentityCard({ initialIdentity }: { initialIdentity: AgentIdentity }) {
  const { data } = useSWR<AgentIdentity>("/api/agent/identity", { fallbackData: initialIdentity, refreshInterval: 60000 });
  const identity = data || initialIdentity;

  return (
    <section className="rounded-lg border border-hairline bg-canvas p-6 shadow-card">
      <div className="flex items-start gap-4">
        <span className="flex h-10 w-10 items-center justify-center rounded-md bg-ink text-white">
          <BadgeCheck size={20} />
        </span>
        <div className="min-w-0">
          <p className="font-mono text-xs text-body">ERC-8004 AGENT IDENTITY</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-[-0.6px] text-ink">{identity.name}</h2>
          <p className="mt-2 text-sm leading-6 text-body">{identity.description}</p>
          <div className="mt-4 grid gap-4 text-sm lg:grid-cols-3">
            <div>
              <p className="font-mono text-xs text-mute">Version</p>
              <p className="mt-1 text-ink">{identity.version}</p>
            </div>
            <div>
              <p className="font-mono text-xs text-mute">Identity contract</p>
              <div className="mt-1">{identity.contract_address ? <AddressDisplay address={identity.contract_address} /> : <span className="text-mute">Not configured</span>}</div>
            </div>
            <div>
              <p className="font-mono text-xs text-mute">Decisions</p>
              <p className="mt-1 text-ink">{identity.total_decisions.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
