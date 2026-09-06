import React, { useState } from "react";
import { Search, Globe, ExternalLink, BookOpen, CheckCircle, Sparkles } from "lucide-react";

export const ResearchHub: React.FC = () => {
  const [query, setQuery] = useState(
    "Сравни Kubernetes vs Docker Swarm для small teams на VPS 1 CPU 4GB RAM"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [researchData, setResearchData] = useState<any>(null);

  const handleResearch = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/command-center/research-worker", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResearchData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-3 border-b border-slate-800">
        <h2 className="text-lg font-mono font-semibold text-slate-100 flex items-center">
          <Search className="w-5 h-5 mr-2 text-emerald-400" />
          Autonomous Research Hub (M4)
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          Web Search Worker • Fact Aggregation • Synthesizer with Grounded Citations
        </p>
      </div>

      {/* Query Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
        <label className="text-xs font-mono text-slate-300 block font-semibold">
          Тема исследования (/research):
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-emerald-500"
            placeholder="Введите тему исследования..."
          />
          <button
            onClick={handleResearch}
            disabled={isLoading || !query.trim()}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-xs font-mono font-semibold transition flex items-center justify-center space-x-2 whitespace-nowrap"
          >
            {isLoading ? (
              <span>Сбор данных & Синтез...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Запустить исследование</span>
              </>
            )}
          </button>
        </div>

        <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
          <span>Шаблоны:</span>
          <button
            onClick={() =>
              setQuery(
                "Сравни Kubernetes vs Docker Swarm для small teams на VPS 1 CPU 4GB RAM"
              )
            }
            className="underline hover:text-slate-200"
          >
            K8s vs Swarm на 4GB VPS
          </button>
          <span>•</span>
          <button
            onClick={() =>
              setQuery("Лучшие практики настройки UFW и Fail2ban на Ubuntu 26.04")
            }
            className="underline hover:text-slate-200"
          >
            UFW + Fail2ban Best Practices
          </button>
          <span>•</span>
          <button
            onClick={() =>
              setQuery("Стратегия бэкапов PostgreSQL через pg_dump и restic")
            }
            className="underline hover:text-slate-200"
          >
            Postgres + Restic бэкапы
          </button>
        </div>
      </div>

      {/* Results */}
      {researchData ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Synthesized Report */}
          <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-mono font-semibold text-slate-100">
                  Синтезированный аналитический отчёт
                </h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                Grounded Citations
              </span>
            </div>

            <div className="text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
              {researchData.report}
            </div>
          </div>

          {/* Sources List */}
          <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-xs font-mono font-semibold text-slate-200 flex items-center">
                <Globe className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
                Верифицированные источники ({researchData.sources?.length || 0})
              </span>
            </div>

            <div className="space-y-2.5">
              {researchData.sources?.map((s: any) => (
                <div
                  key={s.index}
                  className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono space-y-1 hover:border-slate-700 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-400 font-bold">[{s.index}]</span>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-400 hover:text-emerald-400 flex items-center space-x-1"
                    >
                      <span className="text-[10px]">Ссылка</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <div className="text-slate-200 font-semibold">{s.title}</div>
                  <p className="text-[11px] text-slate-400 font-sans">{s.snippet}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500 font-mono text-xs">
          Запустите исследование для демонстрации работы Web Search Worker, извлечения фактов и генерации структурированного отчёта с пронумерованными источниками.
        </div>
      )}
    </div>
  );
};
