from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="fixed-window-best-sum",
        title="Best Sum of a Fixed Window",
        topic="sliding-window",
        tags=["sliding-window", "array"],
        difficulty="easy",
        prompt=(
            "Given a list of integers and a window length k, return the largest "
            "sum of any contiguous block of exactly k values. k is at least 1 and "
            "at most the length of the list."
        ),
        examples=[
            {
                "input": "values = [4, 2, 6, 1, 5, 3], k = 3",
                "output": "12",
                "explanation": "4 + 2 + 6 and 6 + 1 + 5 both sum to 12.",
            }
        ],
        constraints=["The list length is at most 100000."],
        nudge=(
            "Neighboring windows share most of their values. Once you know a "
            "window's sum, what single addition and subtraction produce the next one?"
        ),
        approach=(
            "Compute the sum of the first k values. Then slide: add the value that "
            "enters on the right and subtract the value that leaves on the left. "
            "Track the maximum sum you see. Each index enters and leaves once."
        ),
        pseudocode=(
            "window = sum of the first k values\n"
            "best = window\n"
            "for right from k to n - 1:\n"
            "    window += values[right] - values[right - k]\n"
            "    best = max(best, window)\n"
            "return best"
        ),
        patterns=["fixed window"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["max-sum-subarray-of-size-k"],
    ),
    problem(
        id="longest-unique-stretch",
        title="Longest Stretch of Unique Characters",
        topic="sliding-window",
        tags=["sliding-window", "string"],
        difficulty="medium",
        prompt=(
            "Given a string, return the length of the longest substring whose "
            "characters are all different. A substring is contiguous. The empty "
            "string has length 0."
        ),
        examples=[
            {
                "input": 'text = "abcbda"',
                "output": "4",
                "explanation": '"cbda" has four distinct characters.',
            },
            {"input": 'text = "bbbb"', "output": "1"},
        ],
        constraints=["The string length is at most 100000."],
        nudge=(
            "Grow a window from the left until a character repeats. Which side of "
            "the window has to move before the window is valid again, and how far?"
        ),
        approach=(
            "Keep a window [left, right] and the last index where each character "
            "was seen. When the character at right was already seen inside the "
            "window, jump left to one past that previous index. The window length "
            "right - left + 1 is then a candidate. Each endpoint only moves forward."
        ),
        pseudocode=(
            "last = empty map from character to index\n"
            "left = 0\n"
            "best = 0\n"
            "for right, ch in the string:\n"
            "    if ch was seen at an index >= left:\n"
            "        left = last[ch] + 1\n"
            "    last[ch] = right\n"
            "    best = max(best, right - left + 1)\n"
            "return best"
        ),
        patterns=["variable window"],
        target_time="O(n)",
        target_space="O(1)",
        complexity_note=(
            "The map is bounded by the alphabet, so extra space is constant for a fixed character set."
        ),
        aliases=["longest-substring-without-repeating-characters"],
    ),
    problem(
        id="shortest-covering-window",
        title="Shortest Window That Covers a Pattern",
        topic="sliding-window",
        tags=["sliding-window", "string"],
        difficulty="hard",
        prompt=(
            "You are given a source string and a pattern string. Return the shortest "
            "contiguous slice of the source that contains every character of the "
            "pattern, with at least the required multiplicity. Characters that the "
            "pattern does not mention may appear in the slice. If no slice works, "
            "return an empty string. When several slices share the shortest length, "
            "return any one of them."
        ),
        examples=[
            {
                "input": 'source = "abdxabcx", pattern = "abc"',
                "output": '"abc"',
            }
        ],
        constraints=[
            "The source length is at most 100000.",
            "The pattern length is at most 100000.",
        ],
        nudge=(
            "Expand the right edge until the window covers the pattern. It may now "
            "be longer than necessary. Which characters on the left are safe to drop?"
        ),
        approach=(
            "Count what the pattern still needs. Move the right edge, and whenever "
            "a needed character is satisfied, decrease a counter of missing kinds. "
            "While the window covers everything, record it if it is the shortest so "
            "far, then advance the left edge and give back the character it drops. "
            "Both edges move only forward."
        ),
        pseudocode=(
            "need = counts of characters in the pattern\n"
            "missing = number of distinct characters still short\n"
            "best = an empty range\n"
            "left = 0\n"
            "for right, ch in the source:\n"
            "    consume ch and update missing\n"
            "    while missing is 0:\n"
            "        remember [left, right] if it is shorter than best\n"
            "        give back source[left] and move left\n"
            "return the best slice, or empty"
        ),
        patterns=["cover then shrink"],
        target_time="O(n)",
        target_space="O(1)",
        complexity_note="Extra space is proportional to the alphabet, not to the string length.",
        aliases=["minimum-window-substring"],
    ),
    problem(
        id="rearrangement-window",
        title="Window That Is a Rearrangement",
        topic="sliding-window",
        tags=["sliding-window", "string"],
        difficulty="medium",
        prompt=(
            "Given a source string and a pattern, decide whether any contiguous "
            "slice of the source is a rearrangement of the pattern. The slice must "
            "have the same length as the pattern and the same character counts."
        ),
        examples=[
            {"input": 'source = "eidbaooo", pattern = "ab"', "output": "true"},
            {"input": 'source = "eidboaoo", pattern = "ab"', "output": "false"},
        ],
        constraints=["Both strings have length at most 100000."],
        nudge=(
            "Every candidate slice has the same length as the pattern. How does "
            "the multiset of characters change when the window slides by one?"
        ),
        approach=(
            "Count the pattern. Maintain the count of the current window of that "
            "same length, and also how many characters currently have the exact "
            "required count. Slide one step at a time, updating those two counts "
            "for the character that leaves and the character that enters. If every "
            "tracked character matches, the window is a rearrangement."
        ),
        pseudocode=(
            "if pattern is longer than source: return false\n"
            "need = counts of the pattern\n"
            "have = counts of the first window\n"
            "matched = how many distinct characters already agree\n"
            "if matched covers the pattern alphabet: return true\n"
            "slide the window one character at a time, updating have and matched\n"
            "return whether matched ever covers the pattern"
        ),
        patterns=["fixed window counts"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["permutation-in-string"],
    ),
]
