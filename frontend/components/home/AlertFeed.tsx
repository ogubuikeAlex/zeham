"use client";

import { useMemo, useReducer, useState } from "react";
import { ShieldAlert } from "lucide-react";
import type { Alert, Severity } from "@/types";
import { EmptyState } from "@/components/shared/EmptyState";
import { AlertCard } from "@/components/home/AlertCard";
import { FilterBar } from "@/components/home/FilterBar";
import { useAlertSocket } from "@/hooks/useWebSocket";

function reducer(state: Alert[], alert: Alert) {
  const withoutDuplicate = state.filter((item) => item.id !== alert.id);
  return [alert, ...withoutDuplicate].slice(0, 50);
}

export function AlertFeed({ initialAlerts }: { initialAlerts: Alert[] }) {
  const [alerts, dispatch] = useReducer(reducer, initialAlerts);
  const [severity, setSeverity] = useState<"ALL" | Severity>("ALL");
  const [type, setType] = useState("ALL");

  useAlertSocket((alert) => {
    dispatch(alert);
    if (alert.severity === "CRITICAL") {
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Zeham critical alert", { body: alert.reason });
      } else if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
      }
      const original = document.title;
      document.title = "CRITICAL ALERT - Zeham";
      setTimeout(() => {
        document.title = original;
      }, 4000);
    }
  });

  const types = useMemo(() => Array.from(new Set(alerts.map((alert) => alert.anomaly_type))).sort(), [alerts]);
  const visible = alerts.filter((alert) => (severity === "ALL" || alert.severity === severity) && (type === "ALL" || alert.anomaly_type === type));

  return (
    <section className="space-y-4">
      <FilterBar severity={severity} type={type} types={types} onSeverity={setSeverity} onType={setType} />
      {visible.length ? (
        <div className="space-y-3">
          {visible.map((alert) => <AlertCard key={alert.id} alert={alert} />)}
        </div>
      ) : (
        <EmptyState icon={ShieldAlert} title="No alerts yet" message="Zeham is watching. Alerts will appear here when anomalies are detected." />
      )}
    </section>
  );
}
