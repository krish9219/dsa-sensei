from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="best-contiguous-sum",
        title="Best Contiguous Sum",
        topic="arrays",
        tags=["array", "running-sum"],
        difficulty="medium",
        prompt=(
            "A list of integers may contain negatives. Return the largest sum of "
            "any contiguous slice. The slice must contain at least one value. You "
            "do not need to return the slice itself, only the sum."
        ),
        examples=[
            {
                "input": "values = [-2, 3, -1, 4, -6, 2]",
                "output": "6",
                "explanation": "3 + -1 + 4 = 6, which beats the later 2.",
            }
        ],
        constraints=["The list contains between 1 and 100000 values."],
        nudge=(
            "Suppose you know the best slice that ends at the previous index. "
            "When is it worth extending that slice, and when should you throw it "
            "away and start over at the current value?"
        ),
        approach=(
            "Keep the best sum of a slice that ends exactly at the current index. "
            "That sum is either the current value alone, or the current value plus "
            "the previous ending sum, whichever is larger. The answer is the "
            "largest ending sum you see. This is a linear scan with a few scalars."
        ),
        pseudocode=(
            "best = ending = first value\n"
            "for each later value x:\n"
            "    ending = max(x, ending + x)\n"
            "    best = max(best, ending)\n"
            "return best"
        ),
        patterns=["best sum ending here"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["maximum-subarray", "kadane"],
    ),
    problem(
        id="product-of-others",
        title="Product of Every Other Value",
        topic="arrays",
        tags=["array", "prefix-product"],
        difficulty="medium",
        prompt=(
            "Given a list of integers, return a new list where position i holds "
            "the product of every value except the one at i. Do not use division. "
            "A linear solution may use the output list as scratch space plus a "
            "few extra scalars."
        ),
        examples=[
            {
                "input": "values = [2, 3, 4, 5]",
                "output": "[60, 40, 30, 24]",
                "explanation": "60 = 3*4*5, 40 = 2*4*5, 30 = 2*3*5, 24 = 2*3*4.",
            }
        ],
        constraints=[
            "The list length is between 2 and 100000.",
            "The products fit in a 64-bit signed integer.",
        ],
        nudge=(
            "The missing factor at i is everything to the left of i times "
            "everything to the right of i. Can you build those two sides with "
            "two sweeps instead of a nested loop?"
        ),
        approach=(
            "First write into the output the product of all values strictly to "
            "the left of each index. Then walk from the right with a running "
            "suffix product and multiply it into each output cell. The input is "
            "never divided, and no second full array is required."
        ),
        pseudocode=(
            "out[0] = 1\n"
            "for i from 1 to n - 1:\n"
            "    out[i] = out[i - 1] * values[i - 1]\n"
            "suffix = 1\n"
            "for i from n - 1 down to 0:\n"
            "    out[i] = out[i] * suffix\n"
            "    suffix = suffix * values[i]\n"
            "return out"
        ),
        patterns=["prefix and suffix products"],
        target_time="O(n)",
        target_space="O(1)",
        complexity_note="Extra space ignores the output list, which the problem allows you to build.",
        aliases=["product-except-self"],
    ),
    problem(
        id="rotate-right",
        title="Rotate a List to the Right",
        topic="arrays",
        tags=["array", "reverse"],
        difficulty="medium",
        prompt=(
            "Rotate a list of integers to the right by k steps, in place. A right "
            "rotation moves the last element to the front and shifts everything "
            "else one position right. k may be larger than the length of the list. "
            "Return nothing; the list itself should change."
        ),
        examples=[
            {
                "input": "values = [1, 2, 3, 4, 5, 6], k = 2",
                "output": "[5, 6, 1, 2, 3, 4]",
            }
        ],
        constraints=[
            "The list length is at most 100000.",
            "k is non-negative.",
        ],
        nudge=(
            "After you reduce k modulo the length, the last k items belong at the "
            "front. Reversing regions of the list can move a block without an extra array."
        ),
        approach=(
            "Let k = k mod n, and do nothing when that is zero. Reverse the whole "
            "list, then reverse the first k items, then reverse the remaining "
            "suffix. Each element moves a constant number of times."
        ),
        pseudocode=(
            "k = k mod n\n"
            "reverse the whole list\n"
            "reverse the slice from 0 inclusive to k exclusive\n"
            "reverse the slice from k inclusive to n exclusive"
        ),
        patterns=["three reversals"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["rotate-array"],
    ),
    problem(
        id="merge-sorted-arrays",
        title="Merge Two Sorted Lists",
        topic="arrays",
        tags=["array", "two-pointers"],
        difficulty="easy",
        prompt=(
            "Two lists are each sorted in non-decreasing order. Return one new "
            "list that contains every element of both, also sorted. You may "
            "allocate the result. Do not modify the inputs."
        ),
        examples=[
            {
                "input": "left = [1, 3, 5], right = [2, 4]",
                "output": "[1, 2, 3, 4, 5]",
            }
        ],
        constraints=["Each input has length at most 10000."],
        nudge=(
            "Both inputs are already ordered. If you look only at the front of "
            "each remaining list, which one should be written next?"
        ),
        approach=(
            "Keep an index into each list. Append the smaller current head, and "
            "advance that index. When one list is exhausted, copy the rest of the "
            "other. This is the merge step used by mergesort."
        ),
        pseudocode=(
            "i = j = 0\n"
            "out = empty list\n"
            "while both lists still have items:\n"
            "    append the smaller of left[i] and right[j]\n"
            "    advance the index you took from\n"
            "append whichever suffix remains\n"
            "return out"
        ),
        patterns=["two-way merge"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["merge-two-sorted-arrays"],
    ),
    problem(
        id="dominating-value",
        title="The Value That Dominates",
        topic="arrays",
        tags=["array", "voting"],
        difficulty="easy",
        prompt=(
            "One value in a non-empty list of integers appears more than half the "
            "time. Return that value. A linear scan that stores only a few integers "
            "is possible; you do not need a frequency map."
        ),
        examples=[
            {
                "input": "values = [2, 1, 2, 2, 3, 2]",
                "output": "2",
            }
        ],
        constraints=[
            "The dominating value is guaranteed to exist.",
            "The list length is at most 100000.",
        ],
        nudge=(
            "If you pair each occurrence of a candidate with a different value and "
            "throw the pair away, which value is guaranteed to survive?"
        ),
        approach=(
            "Keep a candidate and a count. When the count is zero, the current "
            "value becomes the candidate. Otherwise increment the count if the "
            "value matches the candidate, and decrement it if not. Because the "
            "answer occurs more than n/2 times, it is the candidate at the end. "
            "The problem promises a majority, so you do not need a second pass."
        ),
        pseudocode=(
            "candidate = any value\n"
            "count = 0\n"
            "for each value x:\n"
            "    if count is 0:\n"
            "        candidate = x\n"
            "    if x == candidate:\n"
            "        count += 1\n"
            "    else:\n"
            "        count -= 1\n"
            "return candidate"
        ),
        patterns=["majority vote"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["majority-element", "boyer-moore"],
    ),
]
