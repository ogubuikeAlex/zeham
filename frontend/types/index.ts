export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type DetectionSource = "AI" | "RULE";
export type ConnectionState = "connecting" | "connected" | "reconnecting" | "disconnected";

export interface Alert {
  id: string;
  contract_address: string;
  severity: Severity;
  anomaly_type: string;
  reason: string;
  confidence: number | null;
  source: DetectionSource;
  recommended_action?: string | null;
  on_chain_tx?: string | null;
  fired_at: string;
}

export interface AlertStats {
  total_alerts_today: number;
  critical_today: number;
  contracts_monitored: number;
  on_chain_decisions: number;
}

export interface DetectionLog {
  id: string;
  contract_address: string | null;
  prompt: string | null;
  raw_response: string | null;
  event_ids: string[] | null;
  logged_at: string;
  on_chain_tx?: string | null;
}

export interface WatchedContract {
  id: string;
  address: string;
  label: string | null;
  active: boolean;
  added_at: string;
  event_count: number;
}

export interface HeatmapCell {
  contract_address: string;
  contract_label: string | null;
  hour: number;
  alert_count: number;
  worst_severity: Severity;
}

export interface TopOffender {
  contract_address: string;
  contract_label: string | null;
  total_alerts: number;
  critical_count: number;
  high_count: number;
  peak_hour: number;
}

export interface HeatmapResponse {
  cells: HeatmapCell[];
  top_offenders: TopOffender[];
  generated_at: string;
}

export interface AgentIdentity {
  name: string;
  version: string;
  description: string;
  agent_wallet: string;
  contract_address: string;
  deployed_at: string;
  total_decisions: number;
}
