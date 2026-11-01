"""Built-in interview problems. Wording and hints are original to this project."""

from __future__ import annotations

from typing import Any

from dsa_sensei.problems.arrays import PROBLEMS as ARRAYS
from dsa_sensei.problems.binary_search import PROBLEMS as BINARY_SEARCH
from dsa_sensei.problems.dynamic_programming import PROBLEMS as DYNAMIC_PROGRAMMING
from dsa_sensei.problems.graphs import PROBLEMS as GRAPHS
from dsa_sensei.problems.hashing import PROBLEMS as HASHING
from dsa_sensei.problems.linked_lists import PROBLEMS as LINKED_LISTS
from dsa_sensei.problems.sliding_window import PROBLEMS as SLIDING_WINDOW
from dsa_sensei.problems.stacks import PROBLEMS as STACKS
from dsa_sensei.problems.trees import PROBLEMS as TREES
from dsa_sensei.problems.two_pointers import PROBLEMS as TWO_POINTERS

RAW_PROBLEMS: list[dict[str, Any]] = [
    *ARRAYS,
    *TWO_POINTERS,
    *SLIDING_WINDOW,
    *HASHING,
    *BINARY_SEARCH,
    *LINKED_LISTS,
    *STACKS,
    *TREES,
    *GRAPHS,
    *DYNAMIC_PROGRAMMING,
]
