# dsa-sensei

A Socratic tutor for data-structures and algorithms interview prep. It gives you the next hint, not the solution, estimates the complexity of the Python you actually wrote, and brings problems back on a spaced-repetition schedule.

It works fully offline. The same tutor is a CLI (`dsa-sensei`) and an [MCP](https://modelcontextprotocol.io) server, so Claude Code, Cursor, and Codex can quiz you inside the editor.

The built-in set is 50 classic problems across ten topics. Prompts, examples, and hint ladders are written for this project. They are not copied from another platform.

## Quickstart

```bash
pipx install "git+https://github.com/krish9219/dsa-sensei.git"
dsa-sensei practice
```

`uv tool install "git+https://github.com/krish9219/dsa-sensei.git"` does the same thing. From a checkout: `pip install .` or `pip install -e ".[dev]"`.

Python 3.10 or newer.

## A session

```text
$ dsa-sensei show stair-ways
╭──────────────────────────────────────────────────────────────╮
│ Ways to Climb the Stairs  stair-ways                         │
╰──────────────── dynamic-programming · easy ──────────────────╯
You climb a staircase of n steps. Each move you may take 1 step
or 2 steps. Return how many distinct sequences of moves reach
the top. ...

$ dsa-sensei hint stair-ways
╭──────────────────────── nudge  1/3 ──────────────────────────╮
│ To stand on step k you arrived either from k-1 or from k-2.  │
│ If you already knew both of those answers, what would you    │
│ do with them?                                                 │
╰───────────────────────────────────────────────────────────────╯
2 rung(s) left. The next one is more specific, and still not a solution.

$ dsa-sensei analyze climb.py --problem stair-ways
Time         O(2^n)
Space        O(n)
Confidence   medium
Watch-outs
  • Branching recursion without memoization or a visited set looks exponential.
Time estimate looks slower than the catalog target of O(n).

$ dsa-sensei attempt stair-ways --quality good --hints 1
Grade 4 (good).
Next review: 2026-04-02  ·  interval 1 day(s)

$ dsa-sensei review --on 2026-04-02
stair-ways   Ways to Climb the Stairs   dynamic-programming   2026-04-02
```

`dsa-sensei hint stair-ways --level 2` asks for the approach. Level 3 is pseudocode. There is no level 4, and there is no command that prints a finished solution.

## What you get

- **Hint ladder.** Each problem has three hand-written rungs: a nudge, the pattern, then pseudocode. The default command reveals the next rung you have not seen and remembers that in the local study log.
- **Complexity feedback.** An AST walk estimates time and space from loop nesting, recursion shape, sorting, and common container operations. It flags `list.pop(0)`, repeated string `+=`, and branching recursion without a cache. The report says these are heuristics.
- **Spaced repetition.** Attempts are stored in SQLite. Grades use SM-2. Ease starts at 2.5 and is updated after every grade, but it never drops below 1.3. Successful reviews are scheduled after 1 day, then 6 days, then `interval × ease`. A grade below 3 schedules the next review for tomorrow and restarts that interval ladder; it does not restore ease to 2.5. Logging an attempt also clears hint progress, so the next session starts again at the nudge. `review` lists what is due. `progress` breaks that down by topic.
- **CLI.** Typer and Rich. `dsa-sensei list`, `show`, `hint`, `analyze`, `attempt`, `review`, `progress`, `practice`.
- **MCP server.** `dsa-sensei mcp` speaks stdio. Tools: `get_problem`, `list_problems`, `get_hint`, `analyze_complexity`, `record_attempt`, `due_reviews`, `progress`.

Optional hints for a problem that is not in the catalog go through any OpenAI-compatible chat endpoint. That path is off until you set the environment variables below. Custom problems are not added to the review deck in v1.

## MCP

Install the CLI first so `dsa-sensei` is on `PATH`. The server uses the official Python MCP SDK (`MCPServer` in SDK 2, the successor of FastMCP).

Claude Code, in `.mcp.json` at the project root or in `~/.claude.json`:

```json
{
  "mcpServers": {
    "dsa-sensei": {
      "command": "dsa-sensei",
      "args": ["mcp"]
    }
  }
}
```

Cursor, in `~/.cursor/mcp.json` (or the project `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "dsa-sensei": {
      "command": "dsa-sensei",
      "args": ["mcp"]
    }
  }
}
```

Ask the agent to tutor, not to solve: fetch the problem, take one hint rung, and record how the attempt felt. The tool descriptions tell it not to dump a full solution.

## Commands

| Command | What it does |
| --- | --- |
| `dsa-sensei list [--topic T] [--difficulty D]` | Catalog, with new / scheduled / due |
| `dsa-sensei topics` | The ten topics |
| `dsa-sensei show ID` | Statement, examples, constraints. No hints |
| `dsa-sensei hint ID [--level 1\|2\|3]` | One rung. Omit `--level` to open the next one |
| `dsa-sensei hint --custom "…"` | One rung for a problem you typed. Needs the LLM env |
| `dsa-sensei analyze FILE --problem ID` | Heuristic complexity. `FILE` may be `-` for stdin |
| `dsa-sensei attempt ID --quality good --hints 1` | Log a recall grade and schedule the next review |
| `dsa-sensei review [--on YYYY-MM-DD]` | What is due |
| `dsa-sensei practice [--topic T]` | A due card, otherwise a new problem |
| `dsa-sensei progress` | Seen, mastered, due, and streak by topic |
| `dsa-sensei config` | Study-log path and whether custom hints are on |
| `dsa-sensei reset --yes` | Delete the local study log |
| `dsa-sensei mcp` | MCP server on stdin/stdout |

Ids accept the catalog slug or an alias such as `two-sum` or `kadane`.

### Recall grades

SM-2 uses integers 0 through 5. Words map as follows.

| Grade | Word | Meaning |
| --- | --- | --- |
| 0 | `blackout` | No recall |
| 1 | `again` | Wrong, the problem felt familiar |
| 2 | `fuzzy` | Wrong, but the idea came back easily once you saw it |
| 3 | `hard` | Right, with serious effort |
| 4 | `good` | Right, with a hesitation |
| 5 | `easy` or `perfect` | Right, cleanly |

A grade below 3 is due again tomorrow. The ease factor still moves, and it never drops below 1.3. "Mastered" in `progress` means two successful reviews and an interval of at least 6 days.

## Catalog

Fifty problems: arrays, two pointers, sliding window, hashing, binary search, linked lists, stacks, trees, graphs, and dynamic programming. Eighteen are easy, twenty-six medium, six hard. Each record is checked by the schema test: three ordered hint rungs, a known complexity label, unique ids and aliases.

`show` does not reveal the target complexity. `analyze --problem` does, so you can compare your code with the bound the catalog considers appropriate.

## Configuration

| Variable | Role |
| --- | --- |
| `DSA_SENSEI_DB` | SQLite file. Default `$XDG_DATA_HOME/dsa-sensei/sensei.db` or `~/.local/share/dsa-sensei/sensei.db` |
| `DSA_SENSEI_TODAY` | Freeze the scheduler clock (`YYYY-MM-DD`). Useful in tests |
| `DSA_SENSEI_LLM_BASE_URL` | OpenAI-compatible base URL, for example `http://127.0.0.1:11434/v1` |
| `DSA_SENSEI_LLM_MODEL` | Model name. Both this and the base URL must be set, or neither |
| `DSA_SENSEI_LLM_API_KEY` | Optional bearer token. Omit it for a local server |
| `DSA_SENSEI_LLM_TIMEOUT` | Seconds. Default 30 |

`--db` on the CLI overrides `DSA_SENSEI_DB`. The API key is never printed.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest
```

GitHub Actions runs that trio on Python 3.10, 3.11, 3.12, and 3.13. See [CONTRIBUTING.md](CONTRIBUTING.md) for adding a problem.

## Roadmap

- User-written problems in the same review deck
- Complexity checks beyond Python
- Export to Anki
- Timed practice sessions
- Evals for hint quality

## License

[MIT](LICENSE). Copyright 2026 Aravind Pilla.
