import React, { useEffect, useState } from "react";
import { Activity, ShieldAlert, Cpu, HardDrive, Terminal, AlertTriangle, CheckCircle, RefreshCw } from "lucide-react";
import { MetricsData } from "../types";

export const ObservabilityDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/command-center/metrics");
      const data = await res.json();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="p-12 text-center text-slate-500 font-mono text-xs">
        Загрузка телеметрии M6...
      </div>
    );
  }

  const asciiDashboard =
    "╔════════════════════════════════════════════════════════════╗\n" +
    "║             COMMAND CENTER OBSERVABILITY v2.0              ║\n" +
    "╠════════════════════════════════════════════════════════════╣\n" +
    `║ Kill Switch: ${metrics.killSwitch.padEnd(14)} Host CPU: ${metrics.host.cpuPercent}%  RAM: ${metrics.host.ramUsedMb}/${metrics.host.ramTotalMb}MB ║\n` +
    `║ Disk: ${metrics.host.diskUsedPercent}% (${metrics.host.diskFreeGb}GB free)   Latency (avg/p95): ${metrics.performance.avgLatencyMs}ms / ${metrics.performance.p95LatencyMs}ms ║\n` +
    "╠════════════════════════════════════════════════════════════╣\n" +
    "║ FLEET HEALTH & CIRCUIT BREAKER MATRIX                      ║\n" +
    "║  • apricot [10.0.1.12]:  🟢 HEALTHY  | Circuit: CLOSED (0 err)║\n" +
    "║  • peach   [10.0.1.14]:  🟢 HEALTHY  | Circuit: CLOSED (0 err)║\n" +
    "║  • berry   [10.0.1.18]:  🟡 WARNING  | Circuit: CLOSED (1 err)║\n" +
    "╠════════════════════════════════════════════════════════════╣\n" +
    "║ FAILURE CLASSIFICATION (ADR-013):                          ║\n" +
    `║  TRANSIENT: ${String(metrics.errorCounts.TRANSIENT).padEnd(3)} | SECURITY: ${String(metrics.errorCounts.SECURITY).padEnd(3)} | LOCAL_RES: ${String(metrics.errorCounts.LOCAL_RESOURCE).padEnd(3)} | POLICY: ${String(metrics.errorCounts.POLICY_VIOLATION).padEnd(3)} ║\n` +
    "╚════════════════════════════════════════════════════════════╝";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-mono font-semibold text-slate-100 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-emerald-400" />
            Heavy Observability & Metrics (M6)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            In-Process Telemetry • ADR-013 Failure Classification • Low Overhead for 1 CPU / 4GB VPS
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-mono flex items-center space-x-1.5 transition self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-emerald-400" : ""}`} />
          <span>Обновить метрики</span>
        </button>
      </div>

      {/* ASCII Dashboard Card (as rendered in Telegram /dashboard) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <span className="text-xs font-mono font-semibold text-slate-300 flex items-center">
            <Terminal className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
            Telegram ASCII Dashboard (/dashboard output)
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-900 text-slate-400 rounded border border-slate-800">
            Monospace Ready
          </span>
        </div>
        <pre className="p-4 bg-slate-950 text-xs font-mono text-emerald-400 overflow-x-auto leading-tight">
          {asciiDashboard}
        </pre>
      </div>

      {/* Host Resources & Failure Classification Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: TRANSIENT */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>TRANSIENT ERRORS</span>
            <span className="w-2 h-2 rounded-full bg-amber-500" />
          </div>
          <div className="text-2xl font-mono font-bold text-slate-100">
            {metrics.errorCounts.TRANSIENT}
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-1">
            Сетевые сбои, таймауты SSH. Учитываются в окне Circuit Breaker.
          </p>
        </div>

        {/* Card 2: SECURITY */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>SECURITY ALERTS</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
          </div>
          <div className="text-2xl font-mono font-bold text-slate-100">
            {metrics.errorCounts.SECURITY}
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-1">
            Несоответствие SSH ключей, отказ в доступе. Мгновенный алерт.
          </p>
        </div>

        {/* Card 3: LOCAL_RESOURCE */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>LOCAL RESOURCE</span>
            <span className="w-2 h-2 rounded-full bg-blue-500" />
          </div>
          <div className="text-2xl font-mono font-bold text-slate-100">
            {metrics.errorCounts.LOCAL_RESOURCE}
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-1">
            Заполнение диска CC хоста (84%), OOM. Не триггерит remote circuit.
          </p>
        </div>

        {/* Card 4: POLICY_VIOLATION */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>POLICY VIOLATIONS</span>
            <span className="w-2 h-2 rounded-full bg-rose-500" />
          </div>
          <div className="text-2xl font-mono font-bold text-slate-100">
            {metrics.errorCounts.POLICY_VIOLATION}
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-1">
            Попытки выполнения при Kill Switch (STOP_ALL / READ_ONLY).
          </p>
        </div>
      </div>

      {/* Active Alerts Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <span className="text-xs font-mono font-semibold text-slate-200 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-1.5 text-amber-400" />
            Активные алерты с дедупликацией (Окно: 300с)
          </span>
          <span className="text-[10px] font-mono text-slate-400">
            {metrics.alerts.length} активный
          </span>
        </div>

        <div className="space-y-2">
          {metrics.alerts.map((alert) => (
            <div
              key={alert.id}
              className="p-3 bg-slate-950 border border-amber-800/40 rounded-lg flex items-start justify-between text-xs font-mono"
            >
              <div className="flex items-start space-x-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-slate-200 font-semibold">{alert.message}</div>
                  <div className="text-slate-500 text-[11px] mt-0.5">
                    Источник: <span className="text-slate-300">server:{alert.server}</span> • {alert.timeAgo}
                  </div>
                </div>
              </div>
              <span className="px-2 py-0.5 bg-amber-950 text-amber-300 border border-amber-800 rounded text-[10px] font-bold">
                {alert.severity}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
