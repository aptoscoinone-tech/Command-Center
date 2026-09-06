import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, CheckCircle, AlertTriangle, Clock, RefreshCw, Terminal, ShieldAlert } from "lucide-react";
import { ChatMessage, PipelineTrace, ApprovalRequest, KillSwitchState } from "../types";

interface TelegramChatProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => Promise<void>;
  isLoading: boolean;
  onApproveRequest: (id: string, approved: boolean) => Promise<void>;
  selectedTrace: PipelineTrace | null;
  onSelectTrace: (trace: PipelineTrace) => void;
  killSwitch: KillSwitchState;
}

export const TelegramChat: React.FC<TelegramChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
  onApproveRequest,
  selectedTrace,
  onSelectTrace,
  killSwitch,
}) => {
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    const text = inputValue;
    setInputValue("");
    onSendMessage(text);
  };

  const samplePrompts = [
    "Как дела у apricot?",
    "Проведи аудит apricot",
    "Что с дисками?",
    "/dashboard",
    "/stop_all",
    "/resume",
    "/coder Напиши функцию которая парсит логи nginx",
    "/research Сравни Kubernetes vs Docker Swarm для small teams",
    "Перезапусти nginx на apricot", // Triggers RED approval
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-140px)]">
      {/* Telegram Chat Window */}
      <div className="lg:col-span-7 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
        {/* Telegram Header */}
        <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
                <Bot className="w-5 h-5" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-slate-950" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-semibold text-slate-100">
                  Command Center Bot (@cc_orchestrator_bot)
                </h3>
                <span className="px-1.5 py-0.2 bg-blue-950 text-blue-400 border border-blue-800 rounded text-[10px] font-mono">
                  Aiogram 3
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Conversational Control Plane (M2.5) • Policy Engine active
              </p>
            </div>
          </div>

          <div className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-400 flex items-center">
            <span
              className={`w-2 h-2 rounded-full mr-1.5 ${
                killSwitch === "NORMAL"
                  ? "bg-emerald-500"
                  : killSwitch === "READ_ONLY"
                  ? "bg-amber-500"
                  : "bg-rose-500"
              }`}
            />
            {killSwitch}
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-950/50 font-sans">
          {messages.map((msg) => {
            const isUser = msg.sender === "user";
            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                <div className="flex items-end space-x-2 max-w-[85%]">
                  {!isUser && (
                    <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 flex-shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`rounded-2xl px-4 py-3 shadow-md ${
                      isUser
                        ? "bg-blue-600 text-white rounded-br-xs"
                        : "bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-xs"
                    }`}
                  >
                    {/* Render message with basic markdown support */}
                    <div className="text-sm whitespace-pre-wrap leading-relaxed font-sans">
                      {msg.text.includes("```") ? (
                        <div>
                          {msg.text.split("```").map((block, idx) => {
                            if (idx % 2 === 1) {
                              // code block
                              const codeLines = block.startsWith("text\n")
                                ? block.replace(/^text\n/, "")
                                : block;
                              return (
                                <pre
                                  key={idx}
                                  className="my-2 p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-emerald-400 overflow-x-auto"
                                >
                                  {codeLines}
                                </pre>
                              );
                            }
                            return <span key={idx}>{block}</span>;
                          })}
                        </div>
                      ) : (
                        msg.text
                      )}
                    </div>

                    {/* Interactive Approval Card if attached */}
                    {msg.approvalRequest && msg.approvalRequest.status === "PENDING" && (
                      <div className="mt-3 p-3 bg-amber-950/40 border border-amber-800/60 rounded-lg text-amber-200 text-xs">
                        <div className="flex items-center space-x-2 font-mono font-semibold mb-2">
                          <AlertTriangle className="w-4 h-4 text-amber-400" />
                          <span>Требуется подтверждение оператора (M5)</span>
                        </div>
                        <p className="mb-2 text-slate-300">
                          Действие: <code className="text-amber-300 font-mono">{msg.approvalRequest.capability}</code> (Риск: <strong className="text-rose-400">{msg.approvalRequest.risk}</strong>)
                        </p>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => onApproveRequest(msg.approvalRequest!.id, true)}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-mono font-semibold transition"
                          >
                            ✓ Подтвердить
                          </button>
                          <button
                            onClick={() => onApproveRequest(msg.approvalRequest!.id, false)}
                            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-mono transition"
                          >
                            ✕ Отклонить
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Footer metadata */}
                    <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-800/50 text-[10px] text-slate-400 font-mono">
                      <span>{msg.timestamp}</span>
                      {msg.pipelineTrace && (
                        <button
                          onClick={() => onSelectTrace(msg.pipelineTrace!)}
                          className="hover:text-emerald-400 underline underline-offset-2 ml-3 flex items-center"
                        >
                          <Terminal className="w-3 h-3 mr-1" />
                          Трейс пайплайна ({msg.pipelineTrace.executionTimeMs}ms)
                        </button>
                      )}
                    </div>
                  </div>

                  {isUser && (
                    <div className="w-7 h-7 rounded-full bg-blue-700 flex items-center justify-center text-white flex-shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex items-center space-x-2 text-slate-400 text-xs font-mono">
              <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
              <span>Intent Router → Policy Engine → Orchestrator...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Pills */}
        <div className="px-3 py-2 bg-slate-900 border-t border-slate-800 overflow-x-auto no-scrollbar flex space-x-2">
          {samplePrompts.map((prompt, i) => (
            <button
              key={i}
              onClick={() => onSendMessage(prompt)}
              className="px-2.5 py-1 text-[11px] font-mono whitespace-nowrap bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700/60 rounded-full transition"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSubmit} className="p-3 bg-slate-950 border-t border-slate-800 flex space-x-2">
          <input
            id="input-telegram-message"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Напишите сообщение (например, 'Как дела у apricot?' или /dashboard)..."
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-sans"
          />
          <button
            id="btn-send-telegram"
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Pipeline Inspector on Right Column */}
      <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col overflow-hidden">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-mono font-semibold text-slate-200">
              Live Pipeline Inspector
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-400 rounded">
            ADR-009 / ADR-011 / ADR-012
          </span>
        </div>

        {selectedTrace ? (
          <div className="flex-1 overflow-y-auto space-y-3 text-xs font-mono">
            {/* Step 1: Intent Router */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-emerald-400 font-bold">1. Intent Router</span>
                <span className="text-[10px] text-slate-500">{selectedTrace.classificationMethod}</span>
              </div>
              <div className="text-slate-200">
                Intent: <span className="text-amber-400">{selectedTrace.intent}</span>
              </div>
              <div className="text-slate-400 mt-1 flex items-center space-x-2">
                <span>Риск:</span>
                <span
                  className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    selectedTrace.risk === "GREEN"
                      ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                      : selectedTrace.risk === "YELLOW"
                      ? "bg-amber-950 text-amber-300 border border-amber-800"
                      : "bg-rose-950 text-rose-300 border border-rose-800"
                  }`}
                >
                  {selectedTrace.risk}
                </span>
                <span>Цель: {selectedTrace.targetServer || "fleet"}</span>
              </div>
            </div>

            {/* Step 2: Policy Engine */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-blue-400 font-bold">2. Policy Engine</span>
                <span className="text-[10px] text-slate-500">Kill Switch check</span>
              </div>
              {selectedTrace.deniedReason ? (
                <div className="text-rose-400 flex items-center space-x-1">
                  <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>{selectedTrace.deniedReason}</span>
                </div>
              ) : (
                <div className="text-emerald-400 flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Политика пройдена: разрешено к исполнению</span>
                </div>
              )}
            </div>

            {/* Step 3: Capability Registry & Orchestrator */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-purple-400 font-bold">3. Orchestrator (ADR-012)</span>
                <span className="text-[10px] text-slate-500">{selectedTrace.executionTimeMs}ms</span>
              </div>
              <div className="text-slate-300">
                Capabilities:
                <ul className="list-disc list-inside mt-1 text-slate-400">
                  {selectedTrace.requiredCapabilities?.map((c, idx) => (
                    <li key={idx} className="text-purple-300">{c}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Step 4: Machine Facts (ADR-009) */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-cyan-400 font-bold">4. Machine Facts (ADR-009)</span>
                <span className="text-[10px] text-cyan-500">Источник истины</span>
              </div>
              <pre className="mt-1 p-2 bg-slate-900 rounded text-[11px] text-slate-300 overflow-x-auto max-h-44">
                {JSON.stringify(selectedTrace.machineFacts || { status: "OK" }, null, 2)}
              </pre>
            </div>

            {/* Step 5: Synthesizer */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-amber-400 font-bold">5. LLM Synthesizer</span>
                <span className="text-[10px] text-slate-500">gemini-3.8-flash</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Строгое следование фактам без галлюцинаций. При отказе LLM используется детерминированный генератор.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-500">
            <Terminal className="w-8 h-8 mb-2 opacity-50 text-slate-400" />
            <p className="text-xs font-mono">
              Отправьте команду или выберите сообщение для визуализации трейса Intent Router, Policy Engine и Machine Facts.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
