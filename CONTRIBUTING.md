# Contributing to dsa-sensei

Thanks for wanting to make the tutor better. The bar is a small, well-tested change that still refuses to hand over a full solution.

## Setup

Python 3.10 or newer.

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest
```

`pytest` fails if coverage of `dsa_sensei` drops under 90%. Tests isolate themselves with `DSA_SENSEI_DB` and `DSA_SENSEI_TODAY`; they should not touch your real study log.

## Adding a problem

Add a `problem(...)` call in the topic module under `src/dsa_sensei/problems/`. The helper lives in `define.py`. `tests/test_schema.py` loads the whole catalog through the schema, so a bad record fails CI.

A record needs:

- a lowercase slug `id`, unique across ids and aliases
- `topic` from the ten topics in `dsa_sensei.schema.TOPICS`
- `difficulty` of `easy`, `medium`, or `hard`
- an original `prompt` (at least 80 characters). Do not paste another platform's statement, and do not mention that platform
- one to four examples with `input` and `output`
- at least one constraint, tag, and pattern
- exactly three hints, in order: `nudge`, `approach`, `pseudocode`
- `target_time` and `target_space` from the allowed set in `schema.py`

Hints are prose or short pseudocode. No fenced code blocks, and no `class Solution`. The nudge should be a question or an observation. The approach may name the pattern. The pseudocode should stay high-level enough that it is not a pasteable solution.

Aliases are the names people already use (`two-sum`, `kadane`). They must be slugs and must not collide with an id or another alias.

If a slower correct approach is still a fair interview answer, list it in `acceptable_time` and explain the difference in `complexity_note`.

## Tests to add with the problem

You usually do not need a new test if the schema test passes. Add one when the problem exercises a new hint or scheduling behavior. Complexity changes belong in `tests/test_complexity.py` with a small snippet and the expected bound.

## Commit style

Prefer a short subject line that says what changed for a student of the tool. Keep unrelated cleanup out of the same commit.

## Reporting bugs

Include the command, the problem id, and whether `DSA_SENSEI_LLM_*` was set. Do not paste API keys.
