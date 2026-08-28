# GitHub Repository Search Tool

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
| `--min-stars` | Минимальное количество звёзд |
| `--sort` | Сортировка: `stars`, `forks` или `updated` |
| `--order` | Направление сортировки: `asc` или `desc` |
| `--limit` | Сколько репозиториев получить (макс. 100) |
| `--output` | Файл для сохранения: `.csv` или `.json` |

## Примеры / Examples

```bash
python github_search.py --topic ai-agents --min-stars 500
python github_search.py --language python --topic machine-learning --sort updated
python github_search.py --topic playwright --topic pytest --output qa_tools.csv
```

## Планы по развитию / Roadmap

- [ ] Добавить сохранение истории запросов
- [ ] Поддержка авторизации через токен GitHub для увеличения лимита запросов
- [ ] Сравнение трендов по нескольким языкам в одном отчёте

---
*Автор использует официальный публичный GitHub REST API (api.github.com), без скрапинга и без авторизации.*