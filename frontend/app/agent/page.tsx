import { AgentIdentityCard } from "@/components/agent/AgentIdentityCard";
import { DecisionLogTable } from "@/components/agent/DecisionLogTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { getAgentIdentity, getDetectionLogs } from "@/lib/api";

export default async function AgentPage() {
  const [identity, logs] = await Promise.all([getAgentIdentity(), getDetectionLogs()]);

  return (
    <>
      <PageHeader eyebrow="ON-CHAIN DECISION TRAIL" title="Every agent decision remains inspectable.">
        <p>Review the model prompt, raw response, contract context, and the identity contract that anchors Zeham decisions.</p>
      </PageHeader>
      <div className="mx-auto max-w-[1400px] space-y-6 px-4 py-6 lg:px-6">
        <AgentIdentityCard initialIdentity={identity} />
        <DecisionLogTable initialLogs={logs} />
      </div>
    </>
  );
}
