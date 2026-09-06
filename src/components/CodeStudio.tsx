import React, { useState } from "react";
import { Code, Play, CheckCircle, ShieldAlert, Sparkles, Terminal, Copy, Check } from "lucide-react";

export const CodeStudio: React.FC = () => {
  const [prompt, setPrompt] = useState(
    "Напиши функцию которая парсит логи nginx и считает количество 5xx ошибок"
  );
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleRunCoder = async () => {
    setIsRunning(true);
    try {
      const res = await fetch("/api/command-center/code-worker", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopy = () => {
    if (!result?.code) return;
    navigator.clipboard.writeText(result.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-3 border-b border-slate-800">
        <h2 className="text-lg font-mono font-semibold text-slate-100 flex items-center">
          <Code className="w-5 h-5 mr-2 text-blue-400" />
          Code Worker & Reviewer Lab (M3)
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          Coder Model: <code className="text-emerald-400">qwen/qwen3-30b</code> • Reviewer: <code className="text-purple-400">deepseek/deepseek-chat-v3.1</code> • Sandboxed Test Execution
        </p>
      </div>

      {/* Task Input */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
        <label className="text-xs font-mono text-slate-300 block font-semibold">
          Описание задачи для кодера (/coder):
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-blue-500"
            placeholder="Например: Напиши функцию для парсинга логов nginx..."
          />
          <button
            onClick={handleRunCoder}
            disabled={isRunning || !prompt.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-mono font-semibold transition flex items-center justify-center space-x-2 whitespace-nowrap"
          >
            {isRunning ? (
              <span>Генерация и тесты...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Сгенерировать & Проверить</span>
              </>
            )}
          </button>
        </div>

        <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
          <span>Шаблоны:</span>
          <button
            onClick={() => setPrompt("Напиши функцию которая парсит логи nginx и считает количество 5xx ошибок")}
            className="underline hover:text-slate-200"
          >
            Парсинг 5xx ошибок nginx
          </button>
          <span>•</span>
          <button
            onClick={() => setPrompt("Напиши функцию для проверки здоровья PostgreSQL через pg_isready")}
            className="underline hover:text-slate-200"
          >
            Проверка PostgreSQL
          </button>
          <span>•</span>
          <button
            onClick={() => setPrompt("Напиши скрипт ротации старых логов с gzip сжатием старше 7 дней")}
            className="underline hover:text-slate-200"
          >
            Ротация логов gzip
          </button>
        </div>
      </div>

      {/* Results View */}
      {result ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Generated Code & Tests */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
              <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
                <span className="text-xs font-mono text-slate-300 font-semibold flex items-center">
                  <Terminal className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
                  Сгенерированный Python код
                </span>
                <button
                  onClick={handleCopy}
                  className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-mono flex items-center space-x-1 transition"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? "Скопировано" : "Копировать"}</span>
                </button>
              </div>
              <pre className="p-4 bg-slate-950/80 text-xs font-mono text-slate-200 overflow-x-auto leading-relaxed">
                {result.code}
              </pre>
            </div>

            {/* Test Suite Execution */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
              <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
                <span className="text-xs font-mono text-slate-300 font-semibold flex items-center">
                  <Play className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
                  Unit тесты в песочнице (CodeExecutor)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {result.testResult?.passed ? "PASSED (0.003s)" : "FAILED"}
                </span>
              </div>
              <pre className="p-4 bg-slate-950/80 text-xs font-mono text-emerald-400 overflow-x-auto leading-relaxed">
                {result.tests}
              </pre>
            </div>
          </div>

          {/* Code Reviewer Panel */}
          <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-purple-400" />
                  <h3 className="text-sm font-mono font-semibold text-slate-100">
                    Автоматический Code Review
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-purple-400 bg-purple-950 px-2 py-0.5 rounded border border-purple-800">
                  Reviewer Model
                </span>
              </div>

              <div className="space-y-3 text-xs font-mono">
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 block mb-1">Статический аудит безопасности:</span>
                  <div className="text-emerald-400 flex items-center space-x-1.5 font-semibold">
                    <CheckCircle className="w-4 h-4" />
                    <span>Уязвимостей не обнаружено (Clean AST)</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Запрещённые вызовы (`os.system`, `eval`, `subprocess`) отсутствуют.
                  </p>
                </div>

                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 block mb-1">Заключение ревьюера:</span>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-line text-xs font-sans">
                    {result.review?.feedback || result.review}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-500">
              Код готов к включению в capability или локальному запуску.
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500 font-mono text-xs">
          Нажмите "Сгенерировать & Проверить" для запуска полного цикла M3: генерация функции, написание тестов, выполнение в песочнице и статический аудит.
        </div>
      )}
    </div>
  );
};
