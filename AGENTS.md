# AGENTS.md

Instructions for any AI coding agent (Claude Code, Codex, Cursor, Copilot, or similar)
working in this repository. Human-readable context lives in `README.md` — read that
first for what the project is and why it exists.

## Project shape

- Single-file CLI tool: `github_search.py`. Searches GitHub repositories via the
  public REST API (`api.github.com`, unauthenticated) and exports results to CSV or
  JSON.
- Tests live in `tests/test_github_search.py` (pytest).
- No package layout, no `src/` — keep it that way unless the project's scope
  genuinely outgrows a single file. Don't introduce multi-file architecture,
  a web framework, or a database for a CLI script this size.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

No `.env` or secrets required — the tool calls the public GitHub API without
authentication.

## How to verify a change

```bash
pytest
```

`pytest.ini` sets `pythonpath = .`, so the plain `pytest` command works from the
repo root without needing `python -m pytest` or a package install.

All tests are offline: `fetch_repos()` is tested via a mocked `requests.get`
(see `_FakeResponse` in the test file). Do not write tests that hit the live
GitHub API — they would be flaky and burn the unauthenticated rate limit.
The Search API this project calls (`/search/repositories`) has its own,
stricter limit than the general REST API: 10 requests/minute unauthenticated.

CI (`.github/workflows/ci.yml`) runs this same `pytest` command on every push
and pull request to `main`. The `main` branch is protected by a ruleset that
requires the `test` check to pass before merging — direct pushes to `main` are
rejected. Work on a feature branch and open a pull request.

## Safe-change boundaries

- **Do not remove the CSV formula-injection sanitization** in `_sanitize_csv_row()`
  (`github_search.py`). It exists because GitHub API fields like `description` are
  attacker-controlled and can start with `=`, `+`, `-`, or `@`, which spreadsheet
  software interprets as formulas. JSON export is intentionally left unsanitized.
- **Do not change the CSV/JSON export schema** (the `Repo` dataclass fields) without
  updating the corresponding tests — anything consuming `repos.csv`/`repos.json`
  depends on this shape staying stable.
- **Keep existing CLI flags backward-compatible.** `--language`, `--topic`,
  `--min-stars`, `--sort`, `--order`, `--limit`, `--output` are documented in
  `README.md`; renaming or repurposing one is a breaking change and needs an
  explicit decision, not a silent rename.
- **`--limit` must stay bounded to 1–100** and **`--min-stars` must stay
  non-negative** (see `_limit_int` / `_non_negative_int` in `github_search.py`) —
  100 is GitHub Search API's real per-page ceiling.
- **Do not add web scraping.** The project intentionally uses only the official
  public GitHub REST API (see README footer).
- **Do not silently pick an identity/contact string, license, or product direction
  on the maintainer's behalf.** Flag it and ask, or leave it as a follow-up —
  these are owner decisions, not implementation details.

## Out of scope for now

The `README.md` roadmap (query history, GitHub token auth, multi-language trend
comparison) is aspirational, not committed work. Don't implement a roadmap item
unless explicitly asked — check with the maintainer first, since token-based auth
in particular changes the security/config surface (secrets handling, `.env`).
