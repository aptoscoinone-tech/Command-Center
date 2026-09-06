import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { TelegramChat } from "./components/TelegramChat";
import { FleetMonitor } from "./components/FleetMonitor";
import { CodeStudio } from "./components/CodeStudio";
import { ResearchHub } from "./components/ResearchHub";
import { ObservabilityDashboard } from "./components/ObservabilityDashboard";
import { CodebaseExplorer } from "./components/CodebaseExplorer";
import { ChatMessage, KillSwitchState, PipelineTrace, ServerInfo } from "./types";

export function App() {
  const [activeTab, setActiveTab] = useState<string>("chat");
  const [killSwitch, setKillSwitch] = useState<KillSwitchState>("NORMAL");
  const [fleet, setFleet] = useState<ServerInfo[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<PipelineTrace | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg_welcome",
      sender: "bot",
      text:
        "👋 **Добро пожаловать в Command Center v2.0!**\n\n" +
        "Я AI-оркестратор парка серверов на базе Ubuntu 26.04 LTS.\n" +
        "• Задавайте вопросы на естественном языке (например, *«Как дела у apricot?»*, *«Что с дисками?»*)\n" +
        "• Для экстренной защиты используйте `/stop_all`, `/resume`, `/read_only`\n" +
        "• Для генерации и ревью кода: `/coder`\n" +
        "• Для веб-исследований: `/research`",
      timestamp: "10:00",
      pipelineTrace: {
        intent: "system.welcome",
        risk: "GREEN",
        requiredCapabilities: ["system.help"],
        targetServer: null,
        executionTimeMs: 1.2,
        classificationMethod: "system_init",
        machineFacts: { status: "ONLINE", control_plane: "active" },
      },
    },
  ]);

  // Fetch initial fleet and kill switch
  const fetchFleet = async () => {
    try {
      const res = await fetch("/api/command-center/fleet");
      const data = await res.json();
      if (data.fleet) setFleet(data.fleet);
      if (data.killSwitch) setKillSwitch(data.killSwitch);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchFleet();
  }, []);

  const handleKillSwitchChange = async (newState: KillSwitchState) => {
    try {
      const res = await fetch("/api/command-center/kill-switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: newState }),
      });
      const data = await res.json();
      if (data.success) {
        setKillSwitch(newState);
        // Add a notification message in chat
        setMessages((prev) => [
          ...prev,
          {
            id: `msg_ks_${Date.now()}`,
            sender: "bot",
            text:
              newState === "EMERGENCY_STOP"
                ? "🛑 **Kill Switch переключён в EMERGENCY_STOP.** Все capabilities заморожены."
                : newState === "READ_ONLY"
                ? "🔒 **Kill Switch переключён в READ_ONLY.** Изменяющие действия заблокированы."
                : "✅ **Kill Switch переключён в NORMAL.** Все разрешённые capabilities активны.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch("/api/command-center/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();

      const botMsg: ChatMessage = {
        id: `msg_b_${Date.now()}`,
        sender: "bot",
        text: data.answer || "Запрос выполнен.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        pipelineTrace: data.pipelineTrace,
        approvalRequest: data.approvalRequest,
      };

      setMessages((prev) => [...prev, botMsg]);
      if (data.pipelineTrace) {
        setSelectedTrace(data.pipelineTrace);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: `msg_err_${Date.now()}`,
          sender: "bot",
          text: "❌ Ошибка связи с бэкендом Command Center.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
      fetchFleet();
    }
  };

  const handleApproveRequest = async (id: string, approved: boolean) => {
    try {
      const res = await fetch("/api/command-center/approval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, approved }),
      });
      const data = await res.json();

      // Update approval status in messages
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.approvalRequest && msg.approvalRequest.id === id) {
            return {
              ...msg,
              approvalRequest: {
                ...msg.approvalRequest,
                status: approved ? "APPROVED" : "DENIED",
              },
            };
          }
          return msg;
        })
      );

      // Add feedback message
      setMessages((prev) => [
        ...prev,
        {
          id: `msg_appr_res_${Date.now()}`,
          sender: "bot",
          text: approved
            ? "✅ **Действие подтверждено оператором (M5).** Оркестратор успешно выполнил команду на сервере."
            : "❌ **Действие отклонено оператором (M5).** Выполнение команды отменено.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
      <Header
        killSwitch={killSwitch}
        onKillSwitchChange={handleKillSwitchChange}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === "chat" && (
          <TelegramChat
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onApproveRequest={handleApproveRequest}
            selectedTrace={selectedTrace}
            onSelectTrace={setSelectedTrace}
            killSwitch={killSwitch}
          />
        )}

        {activeTab === "fleet" && (
          <FleetMonitor
            fleet={fleet}
            onTriggerAction={(cmd) => {
              setActiveTab("chat");
              handleSendMessage(cmd);
            }}
          />
        )}

        {activeTab === "coder" && <CodeStudio />}

        {activeTab === "research" && <ResearchHub />}

        {activeTab === "observability" && <ObservabilityDashboard />}

        {activeTab === "codebase" && <CodebaseExplorer />}
      </main>
    </div>
  );
}
export default App;
