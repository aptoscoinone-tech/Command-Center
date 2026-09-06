export type KillSwitchState = "NORMAL" | "READ_ONLY" | "EMERGENCY_STOP";

export type RiskLevel = "GREEN" | "YELLOW" | "RED";

export interface ServerInfo {
  id: string;
  host: string;
  role: string;
  status: "GREEN" | "YELLOW" | "RED" | "UNKNOWN";
  uptimeDays: number;
  cpuLoad: number;
  ramFreeMb: number;
  ramTotalMb: number;
  diskUsedPercent: number;
  diskFreeGb: number;
  services: string[];
  ports: number[];
  consecutiveFailures: number;
  circuitState: "CLOSED" | "OPEN" | "HALF_OPEN";
  circuitFailuresInWindow: number;
}

export interface PipelineTrace {
  intent: string;
  risk: RiskLevel;
  requiredCapabilities: string[];
  targetServer: string | null;
  machineFacts?: any;
  executionTimeMs: number;
  classificationMethod: string;
  deniedReason?: string;
  failureType?: string;
  status?: string;
}

export interface ApprovalRequest {
  id: string;
  capability: string;
  risk: RiskLevel;
  params: any;
  status: "PENDING" | "APPROVED" | "DENIED" | "EXPIRED";
  createdAt: number;
  expiresAt: number;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  pipelineTrace?: PipelineTrace;
  approvalRequest?: ApprovalRequest;
}

export interface MetricsData {
  timestamp: number;
  host: {
    cpuPercent: number;
    ramUsedMb: number;
    ramTotalMb: number;
    diskUsedPercent: number;
    diskFreeGb: number;
    os: string;
  };
  performance: {
    avgLatencyMs: number;
    p95LatencyMs: number;
    recentSamples: number[];
  };
  errorCounts: {
    TRANSIENT: number;
    SECURITY: number;
    LOCAL_RESOURCE: number;
    POLICY_VIOLATION: number;
  };
  killSwitch: KillSwitchState;
  alerts: Array<{
    id: string;
    severity: "WARNING" | "CRITICAL";
    server: string;
    message: string;
    timeAgo: string;
  }>;
}
