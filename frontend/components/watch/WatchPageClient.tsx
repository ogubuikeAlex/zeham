"use client";

import useSWR from "swr";
import type { WatchedContract } from "@/types";
import { AddContractForm } from "@/components/watch/AddContractForm";
import { WatchedContractsTable } from "@/components/watch/WatchedContractsTable";

export function WatchPageClient({ initialContracts }: { initialContracts: WatchedContract[] }) {
  const { data, mutate } = useSWR<WatchedContract[]>("/api/contracts", { fallbackData: initialContracts });

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 px-4 py-6 lg:px-6">
      <AddContractForm onAdded={() => mutate()} />
      <WatchedContractsTable initialContracts={data || initialContracts} />
    </div>
  );
}
