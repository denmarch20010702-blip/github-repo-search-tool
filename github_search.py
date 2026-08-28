"""
Расширенный поиск репозиториев на GitHub с фильтрами по языку, теме и звёздам.

Примеры запуска:
    python github_search.py --language python --topic automation-testing
    python github_search.py --topic playwright --topic pytest --min-stars 100
    python github_search.py --language python --sort updated --limit 15
"""
import argparse
import csv
import json
from dataclasses import dataclass, asdict

import requests

API_URL = "https://api.github.com/search/repositories"
HEADERS = {
    "User-Agent": "my-portfolio-github-search (contact: example@example.com)",
    "Accept": "application/vnd.github+json",
}


@dataclass
class Repo:
    name: str
    stars: int
    language: str
    topics: str
    url: str
    description: str


def build_query(language: str, topics: list[str], min_stars: int) -> str:
    parts = []

    if language:
        parts.append(f"language:{language}")

    for topic in topics:
        parts.append(f"topic:{topic}")

    if min_stars:
        parts.append(f"stars:>={min_stars}")

    if not parts:
        parts.append("stars:>1000")

    return " ".join(parts)


def fetch_repos(query: str, sort: str, order: str, limit: int) -> list[Repo]:
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": limit,
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [
        Repo(
            name=item["full_name"],
            stars=item["stargazers_count"],
            language=item["language"] or "",
            topics=", ".join(item.get("topics", [])),
            url=item["html_url"],
            description=item["description"] or "",
        )
        for item in data["items"]
    ]


def _sanitize_csv_row(row: dict) -> dict:
    return {
        key: f"'{value}" if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value
        for key, value in row.items()
    }


def save_to_csv(repos: list[Repo], path: str):
    if not repos:
        raise ValueError("save_to_csv() requires a non-empty list of repos")

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(repos[0]).keys()))
        writer.writeheader()
        for repo in repos:
            writer.writerow(_sanitize_csv_row(asdict(repo)))


def save_to_json(repos: list[Repo], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in repos], f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Расширенный поиск GitHub-репозиториев")
    parser.add_argument("--language", help="Язык программирования, например 'python'")
    parser.add_argument(
        "--topic",
        action="append",
        default=[],
        dest="topics",
        help="Тема репозитория, например 'automation-testing'. Можно указывать несколько раз.",
    )
    parser.add_argument("--min-stars", type=int, default=0, help="Минимальное число звёзд")
    parser.add_argument(
        "--sort",
        choices=["stars", "forks", "updated"],
        default="stars",
        help="По чему сортировать результаты",
    )
    parser.add_argument("--order", choices=["asc", "desc"], default="desc")
    parser.add_argument("--limit", type=int, default=10, help="Сколько репозиториев получить (макс. 100)")
    parser.add_argument("--output", default="repos.csv", help="Файл для сохранения: .csv или .json")
    args = parser.parse_args()

    query = build_query(args.language, args.topics, args.min_stars)
    print(f"Поисковый запрос к GitHub: {query}")

    repos = fetch_repos(query, args.sort, args.order, args.limit)
    print(f"Получено репозиториев: {len(repos)}")

    if not repos:
        print("По заданным фильтрам ничего не найдено — попробуй смягчить условия.")
        return

    if args.output.endswith(".json"):
        save_to_json(repos, args.output)
    else:
        save_to_csv(repos, args.output)

    print(f"Сохранено в {args.output}")


if __name__ == "__main__":
    main()