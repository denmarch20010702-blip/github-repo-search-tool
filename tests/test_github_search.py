import csv
import json
import sys

import pytest
import requests

import github_search
from github_search import Repo, build_parser, build_query, fetch_repos, save_to_csv, save_to_json


class _FakeResponse:
    def __init__(self, payload, status_error=None):
        self._payload = payload
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self._payload


def test_build_query_language_only():
    assert build_query("python", [], 0) == "language:python"


def test_build_query_topic_only():
    assert build_query("", ["ai"], 0) == "topic:ai"


def test_build_query_min_stars_only():
    assert build_query("", [], 100) == "stars:>=100"


def test_build_query_default_query():
    assert build_query("", [], 0) == github_search.FALLBACK_QUERY


def test_build_query_all_filters():
    assert build_query("python", ["ai", "ml"], 50) == (
        "language:python topic:ai topic:ml stars:>=50"
    )


def test_build_query_multiple_topics():
    assert build_query("", ["playwright", "pytest"], 0) == (
        "topic:playwright topic:pytest"
    )


def test_build_query_language_and_topic():
    assert build_query("python", ["automation-testing"], 0) == (
        "language:python topic:automation-testing"
    )


def test_build_query_language_and_min_stars():
    assert build_query("python", [], 100) == (
        "language:python stars:>=100"
    )


def test_build_query_topic_and_min_stars():
    assert build_query("", ["pytest"], 100) == (
        "topic:pytest stars:>=100"
    )


def _make_repo(description: str) -> Repo:
    return Repo(
        name="octocat/hello-world",
        stars=42,
        language="python",
        topics="ai, ml",
        url="https://github.com/octocat/hello-world",
        description=description,
    )


@pytest.mark.parametrize(
    "malicious_value",
    [
        '=HYPERLINK("http://evil.example","click")',
        "+1+1",
        "-1+1",
        "@SUM(1,1)",
    ],
)
def test_save_to_csv_sanitizes_formula_injection(tmp_path, malicious_value):
    repo = _make_repo(malicious_value)
    output_path = tmp_path / "repos.csv"

    save_to_csv([repo], str(output_path))

    with open(output_path, newline="", encoding="utf-8-sig") as f:
        row = next(csv.DictReader(f))

    assert row["description"] == f"'{malicious_value}"


def test_save_to_csv_leaves_safe_values_untouched(tmp_path):
    repo = _make_repo("A perfectly normal description")
    output_path = tmp_path / "repos.csv"

    save_to_csv([repo], str(output_path))

    with open(output_path, newline="", encoding="utf-8-sig") as f:
        row = next(csv.DictReader(f))

    assert row["description"] == "A perfectly normal description"


def test_save_to_json_does_not_sanitize_formula_injection(tmp_path):
    malicious_value = '=HYPERLINK("http://evil.example","click")'
    repo = _make_repo(malicious_value)
    output_path = tmp_path / "repos.json"

    save_to_json([repo], str(output_path))

    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data[0]["description"] == malicious_value


def test_save_to_csv_empty_list_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        save_to_csv([], str(tmp_path / "repos.csv"))


def test_fetch_repos_parses_api_response(monkeypatch):
    sample_payload = {
        "items": [
            {
                "full_name": "octocat/hello-world",
                "stargazers_count": 42,
                "language": "Python",
                "topics": ["ai", "ml"],
                "html_url": "https://github.com/octocat/hello-world",
                "description": "A sample repo",
            },
            {
                "full_name": "octocat/no-metadata",
                "stargazers_count": 1,
                "language": None,
                "topics": [],
                "html_url": "https://github.com/octocat/no-metadata",
                "description": None,
            },
        ]
    }
    captured_params = {}

    def fake_get(url, params, headers, timeout):
        captured_params.update(params)
        return _FakeResponse(sample_payload)

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    repos = fetch_repos("language:python", "stars", "desc", 10)

    assert captured_params == {
        "q": "language:python",
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
    }
    assert repos == [
        Repo(
            name="octocat/hello-world",
            stars=42,
            language="Python",
            topics="ai, ml",
            url="https://github.com/octocat/hello-world",
            description="A sample repo",
        ),
        Repo(
            name="octocat/no-metadata",
            stars=1,
            language="",
            topics="",
            url="https://github.com/octocat/no-metadata",
            description="",
        ),
    ]


def test_fetch_repos_raises_on_http_error(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return _FakeResponse({}, status_error=requests.HTTPError("403 Client Error"))

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        fetch_repos("stars:>1000", "stars", "desc", 10)


def test_fetch_repos_returns_empty_list_when_no_items(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return _FakeResponse({"items": []})

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    assert fetch_repos("language:cobol", "stars", "desc", 10) == []


@pytest.mark.parametrize("limit", ["1", "50", "100"])
def test_limit_accepts_values_in_valid_range(limit):
    args = build_parser().parse_args(["--limit", limit])
    assert args.limit == int(limit)


@pytest.mark.parametrize("limit", ["0", "101", "-5"])
def test_limit_rejects_values_out_of_range(limit, capsys):
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--limit", limit])
    assert "must be between 1 and 100" in capsys.readouterr().err


@pytest.mark.parametrize("min_stars", ["0", "100"])
def test_min_stars_accepts_non_negative_values(min_stars):
    args = build_parser().parse_args(["--min-stars", min_stars])
    assert args.min_stars == int(min_stars)


def test_min_stars_rejects_negative_value(capsys):
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--min-stars", "-1"])
    assert "must be a non-negative integer" in capsys.readouterr().err


@pytest.mark.parametrize("output", ["repos.csv", "repos.json", "REPOS.CSV"])
def test_output_accepts_csv_and_json_extensions(output):
    args = build_parser().parse_args(["--output", output])
    assert args.output == output


@pytest.mark.parametrize("output", ["repos.txt", "repos", "repos.csvx"])
def test_output_rejects_unsupported_extensions(output, capsys):
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--output", output])
    assert "must end with .csv or .json" in capsys.readouterr().err


def test_main_happy_path_writes_expected_csv(tmp_path, monkeypatch):
    sample_payload = {
        "items": [
            {
                "full_name": "octocat/hello-world",
                "stargazers_count": 42,
                "language": "Python",
                "topics": ["ai"],
                "html_url": "https://github.com/octocat/hello-world",
                "description": "A sample repo",
            }
        ]
    }

    def fake_get(url, params, headers, timeout):
        return _FakeResponse(sample_payload)

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    output_path = tmp_path / "smoke.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        ["github_search.py", "--language", "python", "--output", str(output_path)],
    )

    github_search.main()

    with open(output_path, newline="", encoding="utf-8-sig") as f:
        row = next(csv.DictReader(f))

    assert row["name"] == "octocat/hello-world"
    assert row["stars"] == "42"
    assert row["url"] == "https://github.com/octocat/hello-world"


def test_main_writes_json_when_output_extension_is_uppercase(tmp_path, monkeypatch):
    sample_payload = {
        "items": [
            {
                "full_name": "octocat/hello-world",
                "stargazers_count": 42,
                "language": "Python",
                "topics": [],
                "html_url": "https://github.com/octocat/hello-world",
                "description": "A sample repo",
            }
        ]
    }

    def fake_get(url, params, headers, timeout):
        return _FakeResponse(sample_payload)

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    output_path = tmp_path / "SMOKE.JSON"
    monkeypatch.setattr(
        sys,
        "argv",
        ["github_search.py", "--language", "python", "--output", str(output_path)],
    )

    github_search.main()

    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data[0]["name"] == "octocat/hello-world"


def test_main_prints_message_and_writes_nothing_when_no_results(tmp_path, monkeypatch, capsys):
    def fake_get(url, params, headers, timeout):
        return _FakeResponse({"items": []})

    monkeypatch.setattr(github_search.requests, "get", fake_get)

    output_path = tmp_path / "smoke.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        ["github_search.py", "--language", "cobol", "--output", str(output_path)],
    )

    github_search.main()

    assert "ничего не найдено" in capsys.readouterr().out
    assert not output_path.exists()