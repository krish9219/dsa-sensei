from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="sorted-lookup",
        title="Look Up a Value in a Sorted List",
        topic="binary-search",
        tags=["binary-search", "array"],
        difficulty="easy",
        prompt=(
            "A list of integers is sorted non-decreasing. Return the index of a "
            "target value, or -1 if it is absent. Use a logarithmic number of "
            "comparisons rather than a linear scan."
        ),
        examples=[
            {"input": "values = [1, 3, 5, 7, 9], target = 7", "output": "3"},
            {"input": "values = [1, 3, 5, 7, 9], target = 4", "output": "-1"},
        ],
        constraints=["The list length is at most 100000."],
        nudge=(
            "The middle value tells you which half can be thrown away. What "
            "invariant do the two endpoints have to keep so you do not skip the target?"
        ),
        approach=(
            "Keep a closed interval [lo, hi] that still might contain the target. "
            "Compare the midpoint with the target and move lo to mid + 1 or hi to "
            "mid - 1. When the interval becomes empty, the target is absent. "
            "Be careful that the midpoint uses integer division and that lo and hi "
            "do not cross without you noticing."
        ),
        pseudocode=(
            "lo, hi = 0, n - 1\n"
            "while lo <= hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if values[mid] == target: return mid\n"
            "    if values[mid] < target: lo = mid + 1\n"
            "    else: hi = mid - 1\n"
            "return -1"
        ),
        patterns=["closed interval"],
        target_time="O(log n)",
        target_space="O(1)",
        aliases=["binary-search"],
    ),
    problem(
        id="insertion-index",
        title="Where a Value Should Be Inserted",
        topic="binary-search",
        tags=["binary-search", "array"],
        difficulty="easy",
        prompt=(
            "A list of distinct integers is sorted ascending. Return the index of "
            "the target if it is present. If it is absent, return the index where "
            "it should be inserted so the list stays sorted. That index may be "
            "equal to the length of the list."
        ),
        examples=[
            {"input": "values = [1, 3, 5, 8], target = 5", "output": "2"},
            {"input": "values = [1, 3, 5, 8], target = 6", "output": "3"},
            {"input": "values = [1, 3, 5, 8], target = 9", "output": "4"},
        ],
        constraints=["The list length is at most 100000."],
        nudge=(
            "You are looking for the first position whose value is greater than or "
            "equal to the target. How does that change the usual equal-or-not branch?"
        ),
        approach=(
            "Search a half-open interval [lo, hi). If the midpoint is less than the "
            "target, the insertion point is to the right. Otherwise it is at mid or "
            "to the left, so keep mid inside the interval. When lo meets hi, lo is "
            "the insertion index, whether or not the target is present."
        ),
        pseudocode=(
            "lo, hi = 0, n\n"
            "while lo < hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if values[mid] < target:\n"
            "        lo = mid + 1\n"
            "    else:\n"
            "        hi = mid\n"
            "return lo"
        ),
        patterns=["lower bound"],
        target_time="O(log n)",
        target_space="O(1)",
        aliases=["search-insert-position"],
    ),
    problem(
        id="rotated-lookup",
        title="Search a Rotated Sorted List",
        topic="binary-search",
        tags=["binary-search", "array"],
        difficulty="medium",
        prompt=(
            "A list of distinct integers was sorted ascending and then rotated some "
            "unknown number of positions. Return the index of a target, or -1 if it "
            "is absent. A linear scan is too slow for the size you should plan for; "
            "aim for a logarithmic search."
        ),
        examples=[
            {
                "input": "values = [6, 7, 1, 2, 3, 4, 5], target = 3",
                "output": "4",
            }
        ],
        constraints=["The list length is at most 10000.", "Values are distinct."],
        nudge=(
            "One half of any midpoint is still fully sorted. How can you tell which "
            "half that is, and whether the target lives inside it?"
        ),
        approach=(
            "On each step, compare the midpoint with the left endpoint to see which "
            "side is the sorted run. If the target lies between that run's ends, "
            "inclusive of the rules you choose, search there. Otherwise search the "
            "other side. The rotation point does not need to be found first."
        ),
        pseudocode=(
            "lo, hi = 0, n - 1\n"
            "while lo <= hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if values[mid] == target: return mid\n"
            "    if values[lo] <= values[mid]:\n"
            "        the left side is sorted; keep it only if target is inside it\n"
            "    else:\n"
            "        the right side is sorted; keep it only if target is inside it\n"
            "return -1"
        ),
        patterns=["sorted half"],
        target_time="O(log n)",
        target_space="O(1)",
        aliases=["search-rotated-sorted-array"],
    ),
    problem(
        id="rotated-minimum",
        title="Smallest Value in a Rotated Sorted List",
        topic="binary-search",
        tags=["binary-search", "array"],
        difficulty="medium",
        prompt=(
            "A list of distinct integers was sorted ascending and then rotated. "
            "Return the smallest value. Use a logarithmic number of comparisons."
        ),
        examples=[
            {"input": "values = [5, 6, 1, 2, 3, 4]", "output": "1"},
            {"input": "values = [1, 2, 3]", "output": "1"},
        ],
        constraints=["The list is non-empty and contains distinct values."],
        nudge=(
            "Compare the midpoint with the right end. Which comparison tells you "
            "that the minimum is in the left half, including the midpoint?"
        ),
        approach=(
            "Keep a half-open or closed interval that still contains the minimum. "
            "If the midpoint is greater than the right endpoint, the rotation point "
            "is strictly to the right of mid. Otherwise the minimum is at mid or to "
            "its left, so the right endpoint can move to mid. Stop when the interval "
            "collapses to one index."
        ),
        pseudocode=(
            "lo, hi = 0, n - 1\n"
            "while lo < hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if values[mid] > values[hi]:\n"
            "        lo = mid + 1\n"
            "    else:\n"
            "        hi = mid\n"
            "return values[lo]"
        ),
        patterns=["compare with the end"],
        target_time="O(log n)",
        target_space="O(1)",
        aliases=["find-minimum-in-rotated-sorted-array"],
    ),
    problem(
        id="lightest-ship",
        title="Lightest Ship That Meets the Deadline",
        topic="binary-search",
        tags=["binary-search", "greedy"],
        difficulty="hard",
        prompt=(
            "Packages must ship in order on one conveyor. Each day you load a "
            "contiguous prefix of the remaining packages without exceeding the "
            "ship's capacity. Given the package weights and a number of days, "
            "return the smallest capacity that lets you finish on time. A package "
            "never weighs more than any feasible capacity."
        ),
        examples=[
            {
                "input": "weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], days = 5",
                "output": "15",
            }
        ],
        constraints=[
            "There is at least one package and at most 50000.",
            "Days is between 1 and the number of packages.",
        ],
        nudge=(
            "If a capacity can finish on time, every larger capacity can too. "
            "What is the smallest capacity you must consider, and the largest?"
        ),
        approach=(
            "Binary search the capacity. The low end is the heaviest single package "
            "and the high end is the sum of all weights. To test a capacity, greedily "
            "fill days from left to right and count how many days you need. If the "
            "count is within the limit, try a smaller capacity; otherwise try a larger one."
        ),
        pseudocode=(
            "lo = max(weights), hi = sum(weights)\n"
            "while lo < hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if greedy_days(weights, mid) <= days:\n"
            "        hi = mid\n"
            "    else:\n"
            "        lo = mid + 1\n"
            "return lo"
        ),
        patterns=["binary search on the answer"],
        target_time="O(n log n)",
        target_space="O(1)",
        complexity_note=(
            "Each capacity test scans the packages once, and the capacity range is the total weight."
        ),
        aliases=["capacity-to-ship-packages"],
    ),
    problem(
        id="median-two-sorted",
        title="Median of Two Sorted Lists",
        topic="binary-search",
        tags=["binary-search", "array"],
        difficulty="hard",
        prompt=(
            "Two lists are each sorted ascending. Return the median of the multiset "
            "you would get by merging them. If the combined length is odd, the median "
            "is the middle value. If it is even, it is the average of the two middle "
            "values. Do this with a logarithmic number of comparisons in the shorter list."
        ),
        examples=[
            {
                "input": "left = [1, 4, 7], right = [2, 5, 9]",
                "output": "4.5",
                "explanation": "The merged list is [1, 2, 4, 5, 7, 9].",
            }
        ],
        constraints=["Each list has length at most 1000.", "Neither list is required to be non-empty."],
        nudge=(
            "You do not need the full merge. A cut in the shorter list implies a cut "
            "in the longer one so the left side has half of the values. What has to "
            "be true of the values on either side of those cuts?"
        ),
        approach=(
            "Binary search the cut in the shorter list. The matching cut in the longer "
            "list is determined by how many values belong on the left half. The cut is "
            "correct when the largest value just left of each cut is less than or equal "
            "to the smallest value just right of the other cut. If the short list's left "
            "value is too big, move its cut left; the mirror case moves it right. The "
            "median is then the max of the left borders, or the average of that and the "
            "min of the right borders when the total count is even."
        ),
        pseudocode=(
            "search a cut i in the shorter list\n"
            "j = half - i, the cut in the longer list\n"
            "left_a, right_a = borders of the short cut, or infinities at the ends\n"
            "left_b, right_b = borders of the long cut\n"
            "if left_a > right_b: the short cut is too far right\n"
            "else if left_b > right_a: the short cut is too far left\n"
            "else: the median is max(lefts), or the average with min(rights) if even"
        ),
        patterns=["partition search"],
        target_time="O(log n)",
        target_space="O(1)",
        aliases=["median-of-two-sorted-arrays"],
    ),
]
