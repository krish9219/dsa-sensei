from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="sorted-pair-sum",
        title="Pair Sum in a Sorted List",
        topic="two-pointers",
        tags=["two-pointers", "array"],
        difficulty="easy",
        prompt=(
            "A list of integers is sorted non-decreasing. Return the indices of "
            "two different positions whose values add up to a target. Exactly one "
            "answer exists. A hash map works, but the sort lets you do it with "
            "constant extra memory."
        ),
        examples=[
            {
                "input": "values = [1, 3, 4, 6, 8, 11], target = 10",
                "output": "[2, 3]",
                "explanation": "4 + 6 = 10.",
            }
        ],
        constraints=["The list length is between 2 and 100000."],
        nudge=(
            "Start one finger at the left end and one at the right. If the sum is "
            "too small, which finger can you move without missing the answer?"
        ),
        approach=(
            "The ends give you the smallest and largest remaining candidates. If "
            "their sum is below the target, the left value is too small for every "
            "partner still inside, so move it right. If the sum is too large, move "
            "the right finger left. Stop when the sum matches."
        ),
        pseudocode=(
            "lo = 0\n"
            "hi = n - 1\n"
            "while lo < hi:\n"
            "    total = values[lo] + values[hi]\n"
            "    if total == target: return lo, hi\n"
            "    if total < target: lo += 1\n"
            "    else: hi -= 1"
        ),
        patterns=["inward pointers"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["two-sum-ii"],
    ),
    problem(
        id="phrase-palindrome",
        title="Phrase Palindrome",
        topic="two-pointers",
        tags=["two-pointers", "string"],
        difficulty="easy",
        prompt=(
            "Decide whether a phrase reads the same forward and backward after you "
            "ignore case and drop every character that is not a letter or digit. "
            "Return true or false. The phrase may be empty, which counts as a palindrome."
        ),
        examples=[
            {
                "input": 'phrase = "Eva, can I see bees in a cave?"',
                "output": "true",
            },
            {
                "input": 'phrase = "hello"',
                "output": "false",
            },
        ],
        constraints=["The phrase length is at most 200000."],
        nudge=(
            "You can clean the string first, but that allocates a second copy. "
            "What if each pointer simply skips characters it is not supposed to compare?"
        ),
        approach=(
            "Put one pointer at each end. Advance either pointer while it sits on "
            "a character that is not a letter or digit. Compare the two characters "
            "case-insensitively, then move both inward. Any mismatch is a no."
        ),
        pseudocode=(
            "lo = 0, hi = n - 1\n"
            "while lo < hi:\n"
            "    move lo forward while it is not alphanumeric\n"
            "    move hi backward while it is not alphanumeric\n"
            "    if lo < hi and lower(s[lo]) != lower(s[hi]): return false\n"
            "    lo += 1; hi -= 1\n"
            "return true"
        ),
        patterns=["inward scan"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["valid-palindrome"],
    ),
    problem(
        id="widest-pool",
        title="Widest Pool Between Two Walls",
        topic="two-pointers",
        tags=["two-pointers", "array"],
        difficulty="medium",
        prompt=(
            "Heights of vertical walls stand on a number line, one wall per index. "
            "Choose two walls. The pool they form has width equal to the distance "
            "between the indices and height equal to the shorter wall. Return the "
            "largest area you can form."
        ),
        examples=[
            {
                "input": "heights = [2, 6, 3, 5, 4]",
                "output": "12",
                "explanation": "The walls of height 6 and 4 are 3 apart, and 3 * 4 = 12.",
            }
        ],
        constraints=["There are between 2 and 100000 walls."],
        nudge=(
            "The widest pair is the two ends, but a short wall wastes the width. "
            "If you must give up some width, which end is the one worth abandoning?"
        ),
        approach=(
            "Start at both ends. The area is limited by the shorter wall. Moving "
            "the taller wall inward cannot beat the current area, because the width "
            "shrinks and the limiter does not grow. Move the shorter wall inward "
            "and keep the best area. Each index is visited once."
        ),
        pseudocode=(
            "lo = 0, hi = n - 1, best = 0\n"
            "while lo < hi:\n"
            "    best = max(best, (hi - lo) * min(height[lo], height[hi]))\n"
            "    if height[lo] <= height[hi]: lo += 1\n"
            "    else: hi -= 1\n"
            "return best"
        ),
        patterns=["shrink the limiter"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["container-with-most-water"],
    ),
    problem(
        id="zero-sum-triplets",
        title="Triplets That Sum to Zero",
        topic="two-pointers",
        tags=["two-pointers", "array"],
        difficulty="medium",
        prompt=(
            "Given a list of integers, return every unique triplet of values that "
            "sums to zero. The same three values should appear once even if several "
            "index choices exist. Order inside a triplet and order among triplets "
            "do not matter."
        ),
        examples=[
            {
                "input": "values = [-2, 0, 1, 1, 2]",
                "output": "[[-2, 0, 2], [-2, 1, 1]]",
            }
        ],
        constraints=["The list length is at most 3000."],
        nudge=(
            "Sorting makes duplicates neighbors and turns the rest of the problem "
            "into a two-sum on a sorted range. How will you skip a value you have "
            "already used as the fixed starting point?"
        ),
        approach=(
            "Sort, then fix one index i and search the suffix with two pointers for "
            "a pair that sums to the negation of values[i]. Skip equal neighbors "
            "for i and for both pointers so each value combination is recorded once. "
            "The sort dominates nothing here; the nested pointer scan is quadratic."
        ),
        pseudocode=(
            "sort values\n"
            "for i from 0 to n - 3:\n"
            "    if i > 0 and values[i] == values[i - 1]: continue\n"
            "    lo, hi = i + 1, n - 1\n"
            "    while lo < hi:\n"
            "        total = values[i] + values[lo] + values[hi]\n"
            "        if total == 0: record the triplet and skip duplicates\n"
            "        else move lo or hi the way a sorted pair-sum would"
        ),
        patterns=["sort then two pointers"],
        target_time="O(n^2)",
        target_space="O(1)",
        complexity_note="Extra space ignores the list of answers.",
        aliases=["three-sum", "3sum"],
    ),
    problem(
        id="trapped-rain",
        title="Rainwater Between Bars",
        topic="two-pointers",
        tags=["two-pointers", "array"],
        difficulty="hard",
        prompt=(
            "Non-negative integers are bar heights standing side by side. Water "
            "above a bar is trapped only up to the shorter of the tallest bar on "
            "its left and the tallest bar on its right, minus the bar's own height. "
            "Return the total trapped water. Bars at the ends hold nothing."
        ),
        examples=[
            {
                "input": "heights = [3, 0, 2, 0, 4]",
                "output": "7",
                "explanation": "The gaps hold 3, 1, and 3 units.",
            }
        ],
        constraints=["There are at most 100000 bars."],
        nudge=(
            "A cell's water level is decided by the weaker of two bounding maxima. "
            "If you know the best wall on the left so far and the best wall on the "
            "right so far, which side is already safe to finalize?"
        ),
        approach=(
            "Keep a pointer at each end, plus the tallest wall seen from each side. "
            "The side whose running maximum is smaller cannot get a higher water "
            "line from the opposite side, so you can add water there and advance "
            "that pointer. Update the running maximum as you go. One pass, constant memory."
        ),
        pseudocode=(
            "lo, hi = 0, n - 1\n"
            "left_max = right_max = 0\n"
            "water = 0\n"
            "while lo < hi:\n"
            "    if heights[lo] <= heights[hi]:\n"
            "        left_max = max(left_max, heights[lo])\n"
            "        water += left_max - heights[lo]\n"
            "        lo += 1\n"
            "    else:\n"
            "        mirror the same steps on the right\n"
            "return water"
        ),
        patterns=["two running maxima"],
        target_time="O(n)",
        target_space="O(1)",
        acceptable_time=["O(n)", "O(n^2)"],
        complexity_note="Precomputing every left and right maximum is also linear, with linear extra space.",
        aliases=["trapping-rain-water"],
    ),
    problem(
        id="push-zeroes-back",
        title="Push Zeroes to the Back",
        topic="two-pointers",
        tags=["two-pointers", "array"],
        difficulty="easy",
        prompt=(
            "Move every zero in a list of integers to the end while keeping the "
            "relative order of the non-zero values. Change the list in place and "
            "do not allocate a second copy of it."
        ),
        examples=[
            {
                "input": "values = [0, 4, 0, 1, 9]",
                "output": "[4, 1, 9, 0, 0]",
            }
        ],
        constraints=["The list length is at most 100000."],
        nudge=(
            "The non-zero values want to pack into a prefix. If you know the next "
            "slot that should hold a non-zero, what do you do when you see one?"
        ),
        approach=(
            "Keep a write index that starts at zero. Scan with a read index. "
            "Whenever the read value is non-zero, write it at the write index and "
            "advance the write index. After the scan, fill the tail with zeroes."
        ),
        pseudocode=(
            "write = 0\n"
            "for each value x:\n"
            "    if x != 0:\n"
            "        values[write] = x\n"
            "        write += 1\n"
            "fill values[write:] with 0"
        ),
        patterns=["read and write index"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["move-zeroes"],
    ),
]
