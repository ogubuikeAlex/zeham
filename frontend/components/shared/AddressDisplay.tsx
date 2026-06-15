"use client";

import { Copy, ExternalLink } from "lucide-react";
import { explorerAddressUrl, truncateMiddle } from "@/lib/formatters";

export function AddressDisplay({ address, label }: { address: string; label?: string | null }) {
  return (
    <span className="inline-flex items-center gap-2">
      <a
        href={explorerAddressUrl(address)}
        target="_blank"
        rel="noreferrer"
        className="font-mono text-sm text-ink hover:text-link"
        title={address}
      >
        {label || truncateMiddle(address)}
      </a>
      <button
        type="button"
        className="rounded-md border border-hairline bg-canvas p-1 text-mute hover:text-ink"
        title="Copy address"
        onClick={() => navigator.clipboard?.writeText(address)}
      >
        <Copy size={14} />
      </button>
      <a href={explorerAddressUrl(address)} target="_blank" rel="noreferrer" className="text-mute hover:text-link" title="Open in explorer">
        <ExternalLink size={14} />
      </a>
    </span>
  );
}
