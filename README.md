# Command Center AI Orchestrator v2.0

AI-оркестратор для автономного и диалогового управления парком удалённых серверов через Telegram и веб-консоль.

**Версия:** 2.0 | **Целевая платформа:** Ubuntu 26.04 LTS (1 CPU, 4GB RAM, 10GB disk)

---

## Архитектурные принципы
- **ADR-009: Machine Truth ≠ LLM Interpretation.** Машинные факты (SSH, Postgres) — непреложный источник истины. LLM выступает лишь интерпретатором.
- **ADR-011: Conversational Control Plane.** Основной интерфейс — свободный текст, slash-команды только для экстренных ситуаций (`/stop_all`, `/resume`, `/read_only`).
- **ADR-012: Declarative Capability Registry.** Каждая операция регистрируется с указанием риска (GREEN, YELLOW, RED), схем и политик в `config/capabilities.yaml`.
- **ADR-013: Failure Classification.** 4 класса сбоев (TRANSIENT, SECURITY, LOCAL_RESOURCE, POLICY_VIOLATION).
- **ADR-014: Human-in-the-loop Approval.** Опасные операции требуют интерактивного подтверждения с таймаутом.
- **ADR-015: Low-Overhead Observability.** Встроенный сборщик метрик без тяжёлых сторонних демонов.

---

## Структура проекта
```
├── app/
│   ├── models.py                  # Dataclasses & Enums (Risk, FailureType, CircuitState)
│   ├── bot.py                     # Aiogram 3 Telegram bot handlers & router
│   ├── services/
│   │   ├── intent_router.py       # Rule-based пре-фильтр + LLM fallback
│   │   ├── policy_engine.py       # Kill switch и Circuit Breaker проверки
│   │   ├── planner.py             # Построение последовательных планов (M2.5)
│   │   ├── multi_step_planner.py  # Декомпозиция задач с зависимостями (M5)
│   │   ├── orchestrator.py        # Выполнение capabilities & сбор machine facts
│   │   ├── synthesizer.py         # LLM & детерминированный синтез ответов (ADR-009)
│   │   ├── context.py             # Менеджер контекста диалога (M5)
│   │   ├── memory.py              # Персистентная память фактов (M5)
│   │   ├── approval.py            # Очередь подтверждения опасных действий (M5)
│   │   ├── metrics.py             # Сбор метрик и latency p95 (M6)
│   │   ├── alerting.py            # Движок алертинга с дедупликацией (M6)
│   │   ├── dashboard.py           # Генератор ASCII и веб-дашбордов (M6)
│   │   ├── code_review.py         # Аудитор сгенерированного кода (M3)
│   │   └── research_synthesizer.py# Синтез веб-исследований с источниками (M4)
│   ├── workers/
│   │   ├── code.py                # Генерация кода, тестов и запуск ревью (M3)
│   │   └── web_search.py          # Поиск и агрегация веб-источников (M4)
│   └── executors/
│       ├── code.py                # Песочница исполнения Python кода (M3)
│       └── ssh.py                 # Forced-command OpenSSH исполнитель
├── config/
│   ├── capabilities.yaml          # Реестр всех capabilities
│   ├── models.yaml                # Конфигурация LLM моделей
│   ├── policies.yaml              # Настройки Kill Switch и лимитов
│   └── remotes.yaml               # Конфигурация серверов (apricot, peach, berry)
├── docs/ADR/                      # Architecture Decision Records
├── migrations/                    # SQL миграции PostgreSQL 18
└── tests/                         # Набор unit & integration тестов
```

---

## Примеры использования
### M2.5 Диалоговое управление:
- `"Как дела у apricot?"` → Возвращает статус GREEN, память, диск, сервисы.
- `"Проведи аудит apricot"` → Запускает аудит портов, SSH и конфигурации.
- `"Что с дисками?"` → Мониторинг заполнения разделов всех серверов.

### Экстренные команды:
- `/stop_all` → Активация EMERGENCY_STOP, мгновенная блокировка всех capabilities.
- `/resume` → Возврат в NORMAL режим.
- `/read_only` → Блокировка изменяющих операций.
- `/dashboard` → ASCII дашборд состояния системы.

### M3 Build / Code:
- `/coder "Напиши функцию которая парсит логи nginx и считает 5xx"` → Код + тесты + авто-ревью.

### M4 Research / Web:
- `/research "Сравни Kubernetes vs Docker Swarm для small teams"` → Отчёт с pros/cons и ссылками.
