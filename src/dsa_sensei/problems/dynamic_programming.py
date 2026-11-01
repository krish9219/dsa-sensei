from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="stair-ways",
        title="Ways to Climb the Stairs",
        topic="dynamic-programming",
        tags=["dynamic-programming", "fibonacci"],
        difficulty="easy",
        prompt=(
            "You climb a staircase of n steps. Each move you may take 1 step or 2 "
            "steps. Return how many distinct sequences of moves reach the top. "
            "Order matters: a single step followed by a double is different from "
            "the reverse. n is at least 1."
        ),
        examples=[
            {
                "input": "n = 3",
                "output": "3",
                "explanation": "1+1+1, 1+2, and 2+1.",
            }
        ],
        constraints=["n is at most 45, so the answer fits in a 32-bit signed integer."],
        nudge=(
            "To stand on step k you arrived either from k-1 or from k-2. If you "
            "already knew both of those answers, what would you do with them?"
        ),
        approach=(
            "Let ways(k) be the number of sequences that reach step k. Then "
            "ways(k) = ways(k - 1) + ways(k - 2), with ways(1) = 1 and ways(2) = 2. "
            "You only need the previous two answers, so the whole computation is "
            "linear time and constant extra memory. The naive recursion repeats the "
            "same subproblems."
        ),
        pseudocode=(
            "if n <= 2: return n\n"
            "prev, curr = 1, 2\n"
            "repeat n - 2 times:\n"
            "    prev, curr = curr, prev + curr\n"
            "return curr"
        ),
        patterns=["linear recurrence"],
        target_time="O(n)",
        target_space="O(1)",
        complexity_note=(
            "The same recurrence written as naive recursion is exponential. Prefer the rolling pair."
        ),
        aliases=["climbing-stairs"],
    ),
    problem(
        id="street-loot",
        title="Maximum Loot Along a Street",
        topic="dynamic-programming",
        tags=["dynamic-programming", "array"],
        difficulty="medium",
        prompt=(
            "Houses on a street hold non-negative amounts of money. You may not rob "
            "two adjacent houses. Return the most money you can take. The street is "
            "a line, not a circle."
        ),
        examples=[
            {
                "input": "houses = [4, 1, 2, 9]",
                "output": "13",
                "explanation": "4 + 9 = 13.",
            }
        ],
        constraints=["There are at most 100 houses."],
        nudge=(
            "At house i you either skip it or take it. If you take it, which earlier "
            "decision are you no longer allowed to use?"
        ),
        approach=(
            "Let best(i) be the best loot using the first i houses. Then best(i) is "
            "the larger of skipping house i-1, which keeps best(i-1), and robbing it, "
            "which adds its money to best(i-2). Two rolling variables replace the array."
        ),
        pseudocode=(
            "take_prev = 0\n"
            "skip_prev = 0\n"
            "for each amount:\n"
            "    robbed = amount + skip_prev\n"
            "    skipped = max(take_prev, skip_prev)\n"
            "    take_prev, skip_prev = robbed, skipped\n"
            "return max(take_prev, skip_prev)"
        ),
        patterns=["take or skip"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["house-robber"],
    ),
    problem(
        id="fewest-coins",
        title="Fewest Coins for an Amount",
        topic="dynamic-programming",
        tags=["dynamic-programming", "unbounded-knapsack"],
        difficulty="medium",
        prompt=(
            "You have coin denominations and a target amount. Return the fewest coins "
            "that sum exactly to the amount. You may use each denomination as many "
            "times as you want. If no combination works, return -1."
        ),
        examples=[
            {
                "input": "coins = [1, 4, 5], amount = 8",
                "output": "2",
                "explanation": "Two 4s make 8.",
            },
            {"input": "coins = [3], amount = 4", "output": "-1"},
        ],
        constraints=[
            "There is at least one denomination and at most 12.",
            "The amount is between 0 and 10000.",
        ],
        nudge=(
            "Suppose you already knew the fewest coins for every smaller amount. "
            "For amount a, which earlier answers would you look at, and what does "
            "an impossible smaller amount do to that choice?"
        ),
        approach=(
            "Let dp[a] be the fewest coins that make amount a. dp[0] is 0. For each "
            "amount from 1 upward, try every coin that does not exceed it and take "
            "one plus dp[amount - coin], ignoring amounts that are still impossible. "
            "If dp[amount] never gets a finite value, the answer is -1. The nested "
            "loops are amount times the number of coins."
        ),
        pseudocode=(
            "dp[0] = 0\n"
            "dp[1..amount] = infinity\n"
            "for a from 1 to amount:\n"
            "    for each coin c that is <= a and dp[a - c] is finite:\n"
            "        dp[a] = min(dp[a], dp[a - c] + 1)\n"
            "return dp[amount], or -1 if it stayed infinite"
        ),
        patterns=["unbounded knapsack"],
        target_time="O(n^2)",
        target_space="O(n)",
        complexity_note="The precise bound is O(amount * number of coins), reported here as O(n^2).",
        aliases=["coin-change"],
    ),
    problem(
        id="longest-rising-subsequence",
        title="Longest Strictly Rising Subsequence",
        topic="dynamic-programming",
        tags=["dynamic-programming", "binary-search"],
        difficulty="medium",
        prompt=(
            "Given a list of integers, return the length of the longest subsequence "
            "that is strictly increasing. The chosen values do not have to be "
            "contiguous, but they must keep their original order."
        ),
        examples=[
            {
                "input": "values = [8, 1, 4, 3, 6, 2, 9]",
                "output": "4",
                "explanation": "One such subsequence is 1, 4, 6, 9.",
            }
        ],
        constraints=["The list length is between 1 and 2500."],
        nudge=(
            "For each index, the best subsequence ending there extends some earlier "
            "subsequence whose last value is smaller. Which earlier answers are legal?"
        ),
        approach=(
            "A direct dynamic program sets dp[i] to 1 plus the best dp[j] among "
            "j < i with values[j] < values[i]. That is quadratic and a solid answer. "
            "A faster method keeps a list of the smallest tail of every increasing "
            "subsequence length found so far, and binary-searches where the current "
            "value can extend or replace a tail. The tails list's length is the answer."
        ),
        pseudocode=(
            "tails = empty list\n"
            "for each value x:\n"
            "    i = lower-bound index of x in tails\n"
            "    if i is past the end: append x\n"
            "    else: tails[i] = x\n"
            "return the length of tails"
        ),
        patterns=["patience tails"],
        target_time="O(n log n)",
        target_space="O(n)",
        acceptable_time=["O(n log n)", "O(n^2)"],
        complexity_note=(
            "The quadratic DP is accepted. The tails list with binary search is the tighter bound."
        ),
        aliases=["longest-increasing-subsequence", "lis"],
    ),
    problem(
        id="edit-distance",
        title="Fewest Edits Between Two Words",
        topic="dynamic-programming",
        tags=["dynamic-programming", "string"],
        difficulty="hard",
        prompt=(
            "You may insert a character, delete a character, or replace a character. "
            "Each edit costs one. Return the fewest edits that turn word a into word b. "
            "Either word may be empty."
        ),
        examples=[
            {
                "input": 'a = "spore", b = "score"',
                "output": "1",
                "explanation": "Replace p with c.",
            },
            {
                "input": 'a = "lead", b = "gold"',
                "output": "3",
            },
        ],
        constraints=["Each word has length at most 500."],
        nudge=(
            "Look at the last characters. If they already match, the rest of the "
            "problem is smaller. If they do not, which three smaller problems "
            "correspond to inserting, deleting, and replacing?"
        ),
        approach=(
            "Let dp[i][j] be the distance between the first i characters of a and "
            "the first j characters of b. The first row and column are the costs of "
            "inserting or deleting everything. If a[i-1] equals b[j-1], dp[i][j] "
            "copies dp[i-1][j-1]. Otherwise it is 1 plus the minimum of the delete, "
            "insert, and replace neighbors. Two rolling rows are enough if you want "
            "linear extra memory."
        ),
        pseudocode=(
            "dp[i][0] = i and dp[0][j] = j\n"
            "for i from 1 to len(a):\n"
            "    for j from 1 to len(b):\n"
            "        if a[i-1] == b[j-1]:\n"
            "            dp[i][j] = dp[i-1][j-1]\n"
            "        else:\n"
            "            dp[i][j] = 1 + min(delete, insert, replace)\n"
            "return dp[len(a)][len(b)]"
        ),
        patterns=["two-string dp"],
        target_time="O(n^2)",
        target_space="O(n^2)",
        acceptable_time=["O(n^2)"],
        complexity_note="n stands for the word lengths; the table is rows times columns.",
        aliases=["levenshtein"],
    ),
]
