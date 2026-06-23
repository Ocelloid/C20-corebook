# Plan — agents-md

Создано: 2026-06-23-22-49

## Цель

Создать `AGENTS.md` в корне репозитория — исчерпывающий онбординг-документ для новых AI-агентов.

## Задачи

- [x] `task-01.md` — Написать AGENTS.md

## Структура файла (архитектурное решение)

```
AGENTS.md
├── 1. Project Overview
├── 2. Repository Structure & Data Pipeline
├── 3. Working with the Translation
│   ├── Source files (pages/, chapters/)
│   ├── Translation output (ru/)
│   └── Quartz wiki (ctd-quartz/content/)
├── 4. Glossary & Terminology (CRITICAL)
├── 5. Translation Rules & Common Mistakes
├── 6. Quartz Site
├── 7. Python Scripts
├── 8. Do NOT Touch
└── 9. Current Status
```

## Критерии готовности

- [ ] Новый агент может понять структуру без дополнительных вопросов
- [ ] Все критические правила терминологии указаны
- [ ] Пайплайн данных описан понятно
- [ ] Quartz описан с командами
- [ ] Файл на английском, стиль инструктивный

## Источники

- `problem.md` — исходные требования
- Отчёт subagent explore — полный анализ репозитория
- `.cursor/rules/` — правила агентов
