import { SeverityHeatmap } from "@/components/heatmap/SeverityHeatmap";
import { TopOffendersTable } from "@/components/heatmap/TopOffendersTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { getHeatmap } from "@/lib/api";

export default async function HeatmapPage() {
  const heatmap = await getHeatmap();

  return (
    <>
      <PageHeader eyebrow="SEVERITY HEATMAP" title="See alert intensity by contract and hour.">
        <p>Scan the contracts driving risk, identify peak windows, and separate noisy low-severity activity from critical bursts.</p>
      </PageHeader>
      <div className="mx-auto max-w-[1400px] space-y-6 px-4 py-6 lg:px-6">
        <SeverityHeatmap initialHeatmap={heatmap} />
        <TopOffendersTable offenders={heatmap.top_offenders} />
      </div>
    </>
  );
}
