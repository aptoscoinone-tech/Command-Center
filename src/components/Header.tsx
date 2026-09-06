import React from "react";
import { Shield, Server, Activity, AlertTriangle, Lock, Power } from "lucide-react";
import { KillSwitchState } from "../types";

interface HeaderProps {
  killSwitch: KillSwitchState;
  onKillSwitchChange: (state: KillSwitchState) => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  killSwitch,
  onKillSwitchChange,
  activeTab,
  onTabChange,
}) => {
  const tabs = [
    { id: "chat", label: "Telegram Bot (M2.5)", badge: "Conversational" },
    { id: "fleet", label: "Fleet & Circuits", badge: "3 Servers" },
    { id: "coder", label: "Code Studio (M3)", badge: "qwen3 / deepseek" },
    { id: "research", label: "Research Hub (M4)", badge: "Web Synthesizer" },
    { id: "observability", label: "Observability (M6)", badge: "Metrics & Alerts" },
    { id: "codebase", label: "Code & ADRs", badge: "32 Files" },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Context */}
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-mono font-bold text-lg">
              CC
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-slate-100 font-semibold text-lg tracking-tight font-mono">
                  Command Center
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-medium bg-emerald-950 text-emerald-300 border border-emerald-800">
                  v2.0
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono hidden sm:block">
                VPS Ubuntu 26.04 LTS • 1 CPU • 4GB RAM • 10GB Disk
              </div>
            </div>
          </div>

          {/* Kill Switch Selector */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 p-1 bg-slate-900 border border-slate-800 rounded-lg">
              <span className="text-xs text-slate-400 px-2 font-mono flex items-center">
                <Shield className="w-3.5 h-3.5 mr-1 text-slate-400" />
                Kill Switch:
              </span>
              <button
                id="btn-killswitch-normal"
                onClick={() => onKillSwitchChange("NORMAL")}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded transition-colors ${
                  killSwitch === "NORMAL"
                    ? "bg-emerald-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                NORMAL
              </button>
              <button
                id="btn-killswitch-readonly"
                onClick={() => onKillSwitchChange("READ_ONLY")}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded transition-colors ${
                  killSwitch === "READ_ONLY"
                    ? "bg-amber-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                READ_ONLY
              </button>
              <button
                id="btn-killswitch-emergencystop"
                onClick={() => onKillSwitchChange("EMERGENCY_STOP")}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded transition-colors ${
                  killSwitch === "EMERGENCY_STOP"
                    ? "bg-rose-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                STOP_ALL
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 overflow-x-auto no-scrollbar py-2 border-t border-slate-800/60">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                onClick={() => onTabChange(tab.id)}
                className={`px-3 py-1.5 text-xs font-mono rounded-md whitespace-nowrap transition-all flex items-center space-x-2 ${
                  isActive
                    ? "bg-slate-800 text-emerald-400 font-semibold border border-slate-700 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded ${
                      isActive
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800/60"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
