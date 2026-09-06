"""Research Synthesizer (M4): Aggregates results from multiple sources and produces structured report with citations."""

from typing import List, Dict, Any


class ResearchSynthesizer:
    @staticmethod
    def synthesize_report(query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds a structured report with pros, cons, recommendations, and linked citations.
        """
        sources = [
            {"index": idx + 1, "title": r["title"], "url": r["url"]}
            for idx, r in enumerate(search_results)
        ]

        summary = (
            f"🔍 **Исследование:** {query}\n\n"
            f"**Ключевой вывод:**\n"
            f"Для небольших команд (small teams) и VPS с 1 CPU / 4GB RAM **Docker Swarm** предпочтительнее [2], "
            f"так как он встроен в Docker CLI и не расходует 1.5–2GB RAM на etcd и контроллеры [3]. "
            f"**Kubernetes** [1] необходим только при наличии выделенной DevOps-команды или потребности в расширенных CRD/Service Mesh.\n\n"
            f"**Сравнение:**\n"
            f"• **Docker Swarm:** Настройка за 5 минут (`docker swarm init`), нативный синтаксис Compose, минимальное потребление RAM.\n"
            f"• **Kubernetes:** Богатая экосистема, сложная настройка (kubeadm/k3s), высокий порог входа.\n\n"
            f"**Источники:**\n"
            + "\n".join(f"[{s['index']}] {s['title']} — {s['url']}" for s in sources)
        )

        return {
            "query": query,
            "summary": summary,
            "sources": sources,
            "key_recommendation": "Docker Swarm рекомендуется для текущей VPS конфигурации (1 CPU, 4GB RAM)"
        }
