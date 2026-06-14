import { ExternalLink } from "lucide-react";
import { explorerTxUrl, truncateMiddle } from "@/lib/formatters";

export function TxHashLink({ tx }: { tx?: string | null }) {
  if (!tx) return <span className="text-mute">No on-chain tx</span>;
  return (
    <a href={explorerTxUrl(tx)} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-mono text-sm text-link">
      {truncateMiddle(tx)}
      <ExternalLink size={14} />
    </a>
  );
}
