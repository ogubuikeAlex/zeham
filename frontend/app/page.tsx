import { AlertFeed } from "@/components/home/AlertFeed";
import { StatsBar } from "@/components/home/StatsBar";
import { PageHeader } from "@/components/shared/PageHeader";
import { getAlerts, getAlertStats } from "@/lib/api";

export default async function HomePage() {
  const [alerts, stats] = await Promise.all([getAlerts(), getAlertStats()]);

  return (
    <>
      <PageHeader eyebrow="LIVE SECURITY OPERATIONS" title="Real-time anomaly feed for watched Mantle contracts.">
        <p>Monitor AI and rule-based detections, confidence, contract context, and ERC-8004 decision records from one compact operations view.</p>
      </PageHeader>
      <div className="mx-auto max-w-[1400px] space-y-6 px-4 py-6 lg:px-6">
        <StatsBar initialStats={stats} />
        <AlertFeed initialAlerts={alerts} />
      </div>
    </>
  );
}
