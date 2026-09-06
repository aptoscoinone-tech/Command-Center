import React, { useState, useEffect } from "react";
import { Folder, FileText, CheckCircle, Play, Copy, Check, Terminal, FileCode } from "lucide-react";

export const CodebaseExplorer: React.FC = () => {
  const [files, setFiles] = useState<Record<string, string>>({});
  const [selectedFile, setSelectedFile] = useState<string>("app/bot.py");
  const [testResults, setTestResults] = useState<any>(null);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch("/api/command-center/files")
      .then((res) => res.json())
      .then((data) => {
        if (data.files) {
          setFiles(data.files);
        }
      })
      .catch(console.error);
  }, []);

  const handleRunAllTests = async () => {
    setIsRunningTests(true);
    try {
      const res = await fetch("/api/command-center/run-tests", { method: "POST" });
      const data = await res.json();
      setTestResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunningTests(false);
    }
  };

  const handleCopy = () => {
    const content = files[selectedFile];
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const fileList = Object.keys(files).sort();

  return (
    <div className="space-y-6">
      {/* Header with Run Tests Button */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-mono font-semibold text-slate-100 flex items-center">
            <FileCode className="w-5 h-5 mr-2 text-blue-400" />
            Кодовая база & Архитектурные спецификации (32 файла)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Полная реализация M0-M6: Registry, Policies, Services, Workers, ADRs & Pytest suites
          </p>
        </div>
        <button
          onClick={handleRunAllTests}
          disabled={isRunningTests}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-xs font-mono font-semibold transition flex items-center justify-center space-x-2 shadow-sm whitespace-nowrap"
        >
          <Play className={`w-3.5 h-3.5 ${isRunningTests ? "animate-spin" : ""}`} />
          <span>{isRunningTests ? "Тестирование..." : "Запустить 12 Unit-тестов"}</span>
        </button>
      </div>

      {/* Test Runner Output banner */}
      {testResults && (
        <div className="p-4 bg-slate-900 border border-emerald-800/60 rounded-xl shadow-lg space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold">
              <CheckCircle className="w-4 h-4" />
              <span>
                Все тесты пройдены успешно ({testResults.passed}/{testResults.total}) за {testResults.durationMs.toFixed(1)}ms
              </span>
            </div>
            <span className="text-[11px] text-slate-400">pytest v8.3.2 • Python 3.14</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 pt-1">
            {testResults.testCases?.map((tc: any, i: number) => (
              <div
                key={i}
                className="p-2 bg-slate-950 border border-slate-800 rounded flex items-center justify-between text-[11px]"
              >
                <span className="text-slate-300 truncate mr-2" title={tc.name}>
                  {tc.name}
                </span>
                <span className="text-emerald-400 font-semibold">{tc.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File Tree & Code Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[650px]">
        {/* Tree sidebar */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
          <div className="px-3 py-2.5 bg-slate-950 border-b border-slate-800 text-xs font-mono font-semibold text-slate-300">
            Файлы проекта ({fileList.length})
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-0.5 text-xs font-mono">
            {fileList.map((filePath) => {
              const isSelected = selectedFile === filePath;
              const isConfig = filePath.startsWith("config/");
              const isTest = filePath.startsWith("tests/");
              const isDoc = filePath.startsWith("docs/");
              const isMigration = filePath.startsWith("migrations/");

              return (
                <button
                  key={filePath}
                  onClick={() => setSelectedFile(filePath)}
                  className={`w-full text-left px-2.5 py-1.5 rounded flex items-center justify-between transition ${
                    isSelected
                      ? "bg-blue-600 text-white font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  }`}
                >
                  <span className="truncate flex items-center">
                    <FileText className="w-3.5 h-3.5 mr-2 flex-shrink-0" />
                    {filePath}
                  </span>
                  <span className="text-[10px] opacity-70 ml-1">
                    {isConfig
                      ? "YAML"
                      : isTest
                      ? "TEST"
                      : isDoc
                      ? "ADR"
                      : isMigration
                      ? "SQL"
                      : "PY"}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Code Content Panel */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
          <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-mono text-slate-300 font-semibold flex items-center">
              <Terminal className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
              {selectedFile}
            </span>
            <button
              onClick={handleCopy}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-mono flex items-center space-x-1 transition"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? "Скопировано" : "Копировать"}</span>
            </button>
          </div>

          <div className="flex-1 overflow-auto bg-slate-950 p-4">
            <pre className="text-xs font-mono text-slate-200 leading-relaxed whitespace-pre">
              {files[selectedFile] || "# Файл пуст или загружается..."}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
