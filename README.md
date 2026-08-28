# GitHub Repository Search Tool

![CI](https://github.com/denmarch20010702-blip/github-repo-search-tool/actions/workflows/ci.yml/badge.svg)

Скрипт для поиска репозиториев на GitHub с гибкими фильтрами: язык программирования, тема, минимальное количество звёзд, сортировка. Результаты сохраняются в CSV или JSON.

*A script for searching GitHub repositories with flexible filters: programming language, topic, minimum stars, sort order. Results are exported to CSV or JSON.*

## Зачем этот проект / Why this project

Реально использую сам, чтобы отслеживать актуальные технологии и интересные проекты по темам вроде автоматизации тестирования и ИИ — не просто учебный пример, а рабочий инструмент.

*Actively used to track relevant technologies and interesting projects in areas like test automation and AI — not just a learning exercise, but a tool I actually use.*

## Стек / Tech stack

- Python 3.11+
- requests (HTTP-запросы к GitHub REST API)
- argparse (гибкий CLI-интерфейс)
- dataclasses (структурированное представление данных)
- pytest (автоматические тесты)

## Как запустить / How to run

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

python github_search.py --language python --topic machine-learning
```

## Аргументы / Arguments

| Аргумент | Описание |
|---|---|
| `--language` | Язык программирования, например `python` |
| `--topic` | Тема репозитория. Можно указывать несколько раз: `--topic pytest --topic playwright` |
| `--min-stars` | Минимальное количество звёзд (неотрицательное целое) |
| `--sort` | Сортировка: `stars`, `forks` или `updated` |
| `--order` | Направление сортировки: `asc` или `desc` |
| `--limit` | Сколько репозиториев получить, от 1 до 100 |
| `--output` | Файл для сохранения: `.csv` или `.json` |

Если не указать ни `--language`, ни `--topic`, ни `--min-stars`, используется fallback-запрос `stars:>1000` — иначе GitHub Search API отклонил бы пустой запрос. Каждый запрос к API ограничен таймаутом 10 секунд.

*If none of `--language`, `--topic`, or `--min-stars` are given, a fallback query `stars:>1000` is used — otherwise the GitHub Search API would reject an empty query. Every API request has a 10-second timeout.*

## Примеры / Examples

```bash
python github_search.py --topic ai-agents --min-stars 500
python github_search.py --language python --topic machine-learning --sort updated
python github_search.py --topic playwright --topic pytest --output qa_tools.csv
```

## Тестирование / Testing

```bash
pytest
```

Тесты покрывают построение поискового запроса, санитизацию CSV-экспорта от инъекции формул, работу с GitHub API через моки (без обращения к сети) и валидацию аргументов CLI. Тот же набор автоматически запускается в CI на каждый push и pull request в `main`; слияние в `main` заблокировано, пока проверки не пройдут.

*Tests cover query building, CSV export sanitization against formula injection, GitHub API interaction (mocked, no live requests), and CLI argument validation. The same suite runs automatically in CI on every push and pull request to `main`; merges into `main` are blocked until checks pass.*

## Для ИИ-агентов / For AI agents

Если вносите изменения с помощью coding-агента (Claude Code, Codex, Cursor и т.п.), см. [`AGENTS.md`](AGENTS.md) — там описаны safe-change границы и порядок проверки.

*If you're contributing via a coding agent (Claude Code, Codex, Cursor, etc.), see [`AGENTS.md`](AGENTS.md) for safe-change boundaries and how to verify changes.*

## Планы по развитию / Roadmap

- [ ] Добавить сохранение истории запросов
- [ ] Поддержка авторизации через токен GitHub для увеличения лимита запросов
- [ ] Сравнение трендов по нескольким языкам в одном отчёте

Краткие спеки для этих пунктов (ожидаемое поведение, формат данных, крайние случаи, способ проверки) — в [`docs/product-context.md`](docs/product-context.md).

*Brief specs for these items (expected behavior, data format, edge cases, verification method) are in [`docs/product-context.md`](docs/product-context.md).*

## Прочее / More

- [`docs/product-context.md`](docs/product-context.md) — сценарии использования, термины, пример вывода, ограничения GitHub Search API.
- [`CHANGELOG.md`](CHANGELOG.md) — заметки о значимых решениях по ходу разработки.
- [`LICENSE`](LICENSE) — MIT.

---
*Автор использует официальный публичный GitHub REST API (api.github.com), без скрапинга и без авторизации.*
