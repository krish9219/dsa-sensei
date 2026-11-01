from __future__ import annotations

import pytest

from dsa_sensei.complexity import (
    Cost,
    analyze_python,
    complexity_key,
    describe_comparison,
    format_cost,
)
from dsa_sensei.errors import CodeRejected
from dsa_sensei.service import analyze_code

NESTED = """
def pairs(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

LINEAR = """
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []
"""

FIB = """
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
"""

FIB_CACHE = """
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
"""

FIB_MANUAL = """
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        result = n
    else:
        result = fib(n - 1, memo) + fib(n - 2, memo)
    memo[n] = result
    return result
"""

SEARCH = """
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""

TREE = """
def depth(node):
    if not node:
        return 0
    return 1 + max(depth(node.left), depth(node.right))
"""

ISLAND = """
def count(grid):
    def dfs(r, c):
        if r < 0 or c < 0 or r >= len(grid) or c >= len(grid[0]) or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    total = 0
    for row in grid:
        for cell in row:
            if cell == "1":
                dfs(0, 0)
                total += 1
    return total
"""

GLUE = """
def glue(words):
    text = ""
    for word in words:
        text += word
    return text
"""

POP = """
def drain(nums):
    while nums:
        nums.pop(0)
"""


def test_loop_nesting_sort_and_sequence() -> None:
    nested = analyze_python(NESTED)
    assert nested.time == "O(n^2)"
    assert nested.space == "O(1)"
    assert nested.confidence == "high"

    linear = analyze_python(LINEAR)
    assert linear.time == "O(n)"
    assert linear.space == "O(n)"

    sequential = analyze_python(
        "def f(nums):\n"
        "    a = 0\n"
        "    for x in nums:\n"
        "        a += x\n"
        "    for x in nums:\n"
        "        a += x\n"
        "    return a\n"
    )
    assert sequential.time == "O(n)"

    copied = analyze_python("def f(nums):\n    return sorted(nums)\n")
    assert copied.time == "O(n log n)"
    assert copied.space == "O(n)"
    inplace = analyze_python("def f(nums):\n    nums.sort()\n")
    assert inplace.time == "O(n log n)"
    assert inplace.space == "O(1)"


def test_recursion_shapes() -> None:
    assert analyze_python(FIB).time == "O(2^n)"
    assert any("exponential" in warning for warning in analyze_python(FIB).warnings)
    assert analyze_python(FIB_CACHE).time == "O(n)"
    assert analyze_python(FIB_MANUAL).time == "O(n)"
    assert analyze_python(TREE).time == "O(n)"
    assert "2^n" not in analyze_python(TREE).time
    search = analyze_python(SEARCH)
    assert search.time == "O(log n)"
    assert search.space == "O(1)"
    island = analyze_python(ISLAND)
    dfs = next(item for item in island.functions if item.name.endswith("dfs"))
    assert dfs.time == "O(n)"
    assert "2^n" not in dfs.time


def test_quadratic_pitfalls_and_rejected_code() -> None:
    glued = analyze_python(GLUE)
    assert glued.time == "O(n^2)"
    assert any("+=" in warning for warning in glued.warnings)
    popped = analyze_python(POP)
    assert popped.time == "O(n^2)"
    assert any("pop(0)" in warning for warning in popped.warnings)
    snippet = analyze_python("total = 0\nfor x in nums:\n    total += x\n")
    assert snippet.primary_function == "<module>"
    assert snippet.time == "O(n)"

    with pytest.raises(CodeRejected, match="line 1"):
        analyze_python("def f(\n")
    with pytest.raises(CodeRejected, match="Submit some Python"):
        analyze_python("   \n\n")
    with pytest.raises(CodeRejected, match="No executable"):
        analyze_python("# just a comment\n")
    with pytest.raises(CodeRejected, match="limited"):
        analyze_python("x = 1\n" * 60_000)
    with pytest.raises(CodeRejected):
        analyze_python(123)  # type: ignore[arg-type]


def test_more_cost_shapes() -> None:
    assert format_cost(Cost(0, 2, 0)) == "O(log^2 n)"
    assert format_cost(Cost(exp=3)) == "O(3^n)"
    assert format_cost(Cost(2, 1, 0)) == "O(n^2 log n)"
    assert complexity_key("O(n + e)") == (0, 1, 0)
    assert complexity_key("O(n^3)") == (0, 3, 0)
    assert complexity_key("O(n^2 log n)") == (0, 2, 1)
    assert complexity_key("not a bound") is None

    mixed = analyze_python(
        "def f(groups):\n"
        "    for group in groups:\n"
        "        group.sort()\n"
        "\n"
        "def helper(x):\n"
        "    return helper(x)\n"
        "\n"
        "class Box:\n"
        "    def push(self, values):\n"
        "        self.items = []\n"
        "        for value in values:\n"
        "            self.items.append(value)\n"
        "        return [value for value in values if value]\n"
    )
    assert mixed.time == "O(n^2 log n)"
    assert any("not inlined" in note for note in mixed.notes)
    assert mixed.confidence == "medium"

    lis = analyze_python(
        "import bisect\n"
        "def length_of_lis(nums):\n"
        "    tails = []\n"
        "    for value in nums:\n"
        "        index = bisect.bisect_left(tails, value)\n"
        "        if index == len(tails):\n"
        "            tails.append(value)\n"
        "        else:\n"
        "            tails[index] = value\n"
        "    return len(tails)\n"
    )
    assert lis.time == "O(n log n)"

    shifted = analyze_python(
        "def rev(nums):\n    out = []\n    for value in nums:\n        out.insert(0, value)\n    return out\n"
    )
    assert shifted.time == "O(n^2)"
    assert any("Inserting" in warning for warning in shifted.warnings)

    joined = analyze_python("def glue(words):\n    return ' '.join(word for word in words if word)\n")
    assert joined.time == "O(n)"
    guarded = analyze_python(
        "def first(nums):\n    try:\n        return nums[0]\n    except IndexError:\n        return 0\n"
    )
    assert guarded.time == "O(1)"


def test_catalog_comparison_is_honest() -> None:
    slow = analyze_code(NESTED, "pair-with-target")
    assert slow["problem_id"] == "pair-with-target"
    assert isinstance(slow["comparison"], str)
    assert "slower" in slow["comparison"]
    fast = analyze_code(LINEAR, "two-sum")
    assert fast["problem_id"] == "pair-with-target"
    assert isinstance(fast["comparison"], str)
    assert "matches" in fast["comparison"]
    plain = analyze_code(LINEAR)
    assert plain["comparison"] is None
    unknown = describe_comparison(
        "O(??)",
        "O(n)",
        ("O(n)",),
        estimate_space="O(1)",
        target_space="O(1)",
        note="",
    )
    assert "could not be compared" in unknown
