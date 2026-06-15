"use client";

import { AlertTriangle } from "lucide-react";
import { EmptyState } from "@/components/shared/EmptyState";

export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="mx-auto max-w-[1400px] px-4 py-10 lg:px-6">
      <EmptyState
        icon={AlertTriangle}
        title="Something went wrong"
        message="The dashboard could not render this section."
        action={<button className="h-9 rounded-md bg-ink px-4 text-sm font-medium text-white" onClick={reset}>Retry</button>}
      />
    </div>
  );
}
