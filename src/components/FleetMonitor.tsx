import React from "react";
import { Server, Activity, HardDrive, Cpu, ShieldCheck, Zap, AlertTriangle, Play } from "lucide-react";
import { ServerInfo } from "../types";

interface FleetMonitorProps {
  fleet: ServerInfo[];
  onTriggerAction: (command: string) => void;
}

export const FleetMonitor: React.FC<FleetMonitorProps> = ({ fleet, onTriggerAction }) => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-mono font-semibold text-slate-100 flex items-center">
            <Server className="w-5 h-5 mr-2 text-emerald-400" />
            Управляемый парк серверов (M1 - M2.2)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            OpenSSH Forced-Command mode • Machine Facts • Per-Server Circuit Breakers (ADR-013)
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="flex items-center text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5" /> 2 Healthy
          </span>
          <span className="flex items-center text-amber-400 ml-3">
            <span className="w-2 h-2 rounded-full bg-amber-500 mr-1.5" /> 1 Warning (Disk 84%)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {fleet.map((server) => {
          const isHealthy = server.status === "GREEN";
          const isWarning = server.status === "YELLOW";

          return (
            <div
              key={server.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 transition rounded-xl p-5 flex flex-col justify-between shadow-lg"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-base font-bold font-mono text-slate-100 uppercase">
                        {server.id}
                      </h3>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                          isHealthy
                            ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                            : isWarning
                            ? "bg-amber-950 text-amber-300 border border-amber-800"
                            : "bg-rose-950 text-rose-300 border border-rose-800"
                        }`}
                      >
                        {server.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">
                      {server.host} • {server.role}
                    </div>
                  </div>

                  {/* Circuit Breaker Pill */}
                  <div
                    className="text-[10px] font-mono px-2 py-1 rounded bg-slate-950 border border-slate-800 flex items-center space-x-1"
                    title="Per-server circuit breaker state"
                  >
                    <Zap className="w-3 h-3 text-amber-400" />
                    <span className="text-slate-300">{server.circuitState}</span>
                  </div>
                </div>

                {/* Metrics Bars */}
                <div className="mt-5 space-y-3.5 text-xs font-mono">
                  {/* Disk */}
                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span className="flex items-center">
                        <HardDrive className="w-3.5 h-3.5 mr-1 text-slate-400" />
                        Диск (/dev/sda1)
                      </span>
                      <span className={server.diskUsedPercent > 80 ? "text-amber-400 font-bold" : "text-slate-300"}>
                        {server.diskUsedPercent}% ({server.diskFreeGb}GB free)
                      </span>
                    </div>
                    <div className="h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className={`h-full rounded-full transition-all ${
                          server.diskUsedPercent > 80 ? "bg-amber-500" : "bg-emerald-500"
                        }`}
                        style={{ width: `${server.diskUsedPercent}%` }}
                      />
                    </div>
                  </div>

                  {/* RAM */}
                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span className="flex items-center">
                        <Cpu className="w-3.5 h-3.5 mr-1 text-slate-400" />
                        RAM
                      </span>
                      <span className="text-slate-300">
                        {server.ramFreeMb}MB свободно / {server.ramTotalMb}MB
                      </span>
                    </div>
                    <div className="h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="h-full bg-blue-500 rounded-full transition-all"
                        style={{
                          width: `${Math.round(
                            ((server.ramTotalMb - server.ramFreeMb) / server.ramTotalMb) * 100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* CPU Load & Uptime */}
                  <div className="grid grid-cols-2 gap-2 pt-1 text-[11px] text-slate-400">
                    <div className="p-2 bg-slate-950 rounded border border-slate-800/80">
                      <span className="text-slate-500 block text-[10px]">CPU LOAD (1m)</span>
                      <span className="text-slate-200 font-semibold">{server.cpuLoad}</span>
                    </div>
                    <div className="p-2 bg-slate-950 rounded border border-slate-800/80">
                      <span className="text-slate-500 block text-[10px]">UPTIME</span>
                      <span className="text-slate-200 font-semibold">{server.uptimeDays} дней</span>
                    </div>
                  </div>

                  {/* Services & Ports */}
                  <div className="pt-1">
                    <span className="text-[10px] text-slate-500 uppercase block mb-1">
                      Активные сервисы ({server.services.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {server.services.map((srv, idx) => (
                        <span
                          key={idx}
                          className="px-1.5 py-0.5 bg-slate-950 border border-slate-800 rounded text-[10px] text-slate-300"
                        >
                          {srv}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => onTriggerAction(`Проверь состояние ${server.id}`)}
                  className="flex-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-mono rounded transition flex items-center justify-center space-x-1"
                >
                  <Activity className="w-3 h-3 text-emerald-400" />
                  <span>Health</span>
                </button>
                <button
                  onClick={() => onTriggerAction(`Проведи аудит ${server.id}`)}
                  className="flex-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-mono rounded transition flex items-center justify-center space-x-1"
                >
                  <ShieldCheck className="w-3 h-3 text-amber-400" />
                  <span>Аудит</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
