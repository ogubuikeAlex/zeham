import { PageHeader } from "@/components/shared/PageHeader";
import { WatchPageClient } from "@/components/watch/WatchPageClient";
import { getContracts } from "@/lib/api";

export default async function WatchPage() {
  const contracts = await getContracts();

  return (
    <>
      <PageHeader eyebrow="WATCHLIST MANAGER" title="Add contracts while the listener keeps running.">
        <p>Validate addresses client-side, submit them to FastAPI, and track the active contracts Zeham monitors.</p>
      </PageHeader>
      <WatchPageClient initialContracts={contracts} />
    </>
  );
}
