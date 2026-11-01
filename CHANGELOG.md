# Changelog

All notable changes to dsa-sensei are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-01

### Added

- Offline catalog of 50 original problems across arrays, two pointers, sliding window, hashing, binary search, linked lists, stacks, trees, graphs, and dynamic programming.
- Three-rung hint ladder (nudge, approach, pseudocode) that never returns a full solution.
- AST heuristic for time and space complexity of Python, including a comparison with the catalog bound.
- SQLite study log with SM-2 scheduling, `review`, `progress`, and `practice`.
- Typer + Rich CLI installed as `dsa-sensei`.
- MCP server (`dsa-sensei mcp`) with tools for problems, hints, complexity, attempts, due reviews, and progress.
- Optional OpenAI-compatible hints for problems outside the catalog, off unless configured.

### Fixed

- Complexity estimates for amortized scans (monotonic stacks, sliding windows, grid flood fills) and constant-size loops.
- LLM hint sanitizer strips fences on every rung and withholds function definitions. Withheld rungs are not cached.
- Hint progress restarts after a logged attempt.
- Problem statements no longer reveal pattern names before the approach rung.
- Study-log writes use an immediate transaction, a busy timeout, and an ordered schema migration.
