"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { watchContract } from "@/lib/api";

const ADDRESS_RE = /^0x[0-9a-fA-F]{40}$/;

export function AddContractForm({ onAdded }: { onAdded: () => void }) {
  const [address, setAddress] = useState("");
  const [label, setLabel] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const error = address && !ADDRESS_RE.test(address) ? "Use a 0x-prefixed 40-hex-character contract address." : null;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!ADDRESS_RE.test(address)) return;
    setSubmitting(true);
    setStatus(null);
    try {
      await watchContract(address, label || undefined);
      setStatus("Contract added to the live watchlist.");
      setAddress("");
      setLabel("");
      onAdded();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Could not add contract.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={submit} className="rounded-lg border border-hairline bg-canvas p-5 shadow-card">
      <div className="grid gap-3 lg:grid-cols-[1fr_260px_auto]">
        <div>
          <label className="font-mono text-xs text-body" htmlFor="address">Contract address</label>
          <input id="address" value={address} onChange={(event) => setAddress(event.target.value)} className="mt-2 h-10 w-full rounded-md border border-hairline bg-canvas px-3 font-mono text-sm text-ink" placeholder="0x..." />
          {error ? <p className="mt-2 text-sm text-error">{error}</p> : null}
        </div>
        <div>
          <label className="font-mono text-xs text-body" htmlFor="label">Label</label>
          <input id="label" value={label} onChange={(event) => setLabel(event.target.value)} className="mt-2 h-10 w-full rounded-md border border-hairline bg-canvas px-3 text-sm text-ink" placeholder="Mantle DEX" />
        </div>
        <button type="submit" disabled={Boolean(error) || !address || submitting} className="mt-6 inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-hairline-strong">
          <Plus size={16} />
          {submitting ? "Adding" : "Watch"}
        </button>
      </div>
      {status ? <p className="mt-3 text-sm text-body">{status}</p> : null}
    </form>
  );
}
