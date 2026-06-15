"use client";

import type { TopOffender } from "@/types";
import { AddressDisplay } from "@/components/shared/AddressDisplay";

export function TopOffendersTable({ offenders }: { offenders: TopOffender[] }) {
  if (!offenders.length) return null;

  return (
    <section className="overflow-hidden rounded-lg border border-hairline bg-canvas shadow-card">
      <div className="border-b border-hairline px-5 py-4">
        <h2 className="text-lg font-semibold tracking-[-0.3px] text-ink">Top offenders</h2>
      </div>
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-canvas-soft font-mono text-xs text-body">
          <tr>
            <th className="border-b border-hairline px-4 py-3 font-normal">Contract</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Total</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Critical</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">High</th>
            <th className="border-b border-hairline px-4 py-3 font-normal">Peak hour</th>
          </tr>
        </thead>
        <tbody>
          {offenders.map((offender) => (
            <tr key={offender.contract_address} className="border-b border-hairline last:border-b-0">
              <td className="px-4 py-4"><AddressDisplay address={offender.contract_address} label={offender.contract_label} /></td>
              <td className="px-4 py-4 text-body">{offender.total_alerts}</td>
              <td className="px-4 py-4 text-error">{offender.critical_count}</td>
              <td className="px-4 py-4 text-orange-700">{offender.high_count}</td>
              <td className="px-4 py-4 font-mono text-xs text-body">{String(offender.peak_hour).padStart(2, "0")}:00</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
