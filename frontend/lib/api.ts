import type { AgentIdentity, Alert, AlertStats, DetectionLog, HeatmapResponse, WatchedContract } from "@/types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

async function fetchJson<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      ...init,
      signal: controller.signal,
      cache: "no-store",
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) }
    });
    if (!res.ok) return fallback;
    return (await res.json()) as T;
  } catch {
    return fallback;
  } finally {
    clearTimeout(timer);
  }
}

export const emptyStats: AlertStats = {
  total_alerts_today: 0,
  critical_today: 0,
  contracts_monitored: 0,
  on_chain_decisions: 0
};

export function getAlerts() {
  return fetchJson<Alert[]>("/alerts?limit=50", []);
}

export async function getAlertStats() {
  const stats = await fetchJson<Partial<AlertStats> & Record<string, unknown>>(
    "/alerts/stats",
    emptyStats as Partial<AlertStats> & Record<string, unknown>
  );
  return {
    total_alerts_today: Number(stats.total_alerts_today ?? stats.total_alerts ?? 0),
    critical_today: Number(stats.critical_today ?? stats.critical_count ?? 0),
    contracts_monitored: Number(stats.contracts_monitored ?? stats.watching ?? 0),
    on_chain_decisions: Number(stats.on_chain_decisions ?? stats.decisions_logged ?? 0)
  };
}

export function getDetectionLogs() {
  return fetchJson<DetectionLog[]>("/agent/log", []);
}

export function getContracts() {
  return fetchJson<WatchedContract[]>("/contracts", []);
}

export async function watchContract(address: string, label?: string) {
  const result = await fetch("/api/contracts/watch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address, label })
  });
  if (!result.ok) throw new Error((await result.text()) || "Could not watch contract");
  return result.json();
}

export function getHeatmap() {
  return fetchJson<HeatmapResponse>("/heatmap", { cells: [], top_offenders: [], generated_at: new Date().toISOString() });
}

export async function getAgentIdentity(): Promise<AgentIdentity> {
  const fallback: AgentIdentity = {
    name: "Zeham Mantis Agent",
    version: "0.1.0",
    description: "On-chain AI security monitor logging anomaly decisions through ERC-8004.",
    agent_wallet: "",
    contract_address: process.env.NEXT_PUBLIC_ERC8004_ADDRESS || "",
    deployed_at: "",
    total_decisions: 0
  };
  return fetchJson<AgentIdentity>("/agent/identity", fallback);
}
