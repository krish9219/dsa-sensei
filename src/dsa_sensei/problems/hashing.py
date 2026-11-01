from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="pair-with-target",
        title="Pair With a Target Sum",
        topic="hashing",
        tags=["hash-map", "array"],
        difficulty="easy",
        prompt=(
            "You are given a list of integers and a target sum. Return the indices of "
            "two different positions whose values add up to the target. Exactly one "
            "answer exists, and you may return the indices in either order. The same "
            "position may not be used twice."
        ),
        examples=[
            {
                "input": "values = [4, 1, 8, 3], target = 11",
                "output": "[2, 3]",
                "explanation": "8 + 3 = 11.",
            }
        ],
        constraints=[
            "There are between 2 and 10000 values.",
            "Exactly one pair sums to the target.",
        ],
        nudge=(
            "A double scan finds the pair, but you can do better if you remember "
            "what you have already seen. For the current number, what single partner "
            "would finish the target?"
        ),
        approach=(
            "Walk left to right and keep a map from a value to the index where you "
            "saw it. Before storing the current value x, ask whether target - x is "
            "already in the map. That lookup is expected to be constant time, so the "
            "whole pass is linear."
        ),
        pseudocode=(
            "seen = empty map from value to index\n"
            "for each index i and value x:\n"
            "    partner = target - x\n"
            "    if partner is in seen:\n"
            "        return seen[partner] and i\n"
            "    seen[x] = i"
        ),
        patterns=["complement lookup"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["two-sum"],
    ),
    problem(
        id="cluster-scrambles",
        title="Cluster Word Scrambles",
        topic="hashing",
        tags=["hash-map", "string"],
        difficulty="medium",
        prompt=(
            "You are given lowercase words. Group together the words that are "
            "rearrangements of one another. Order among groups does not matter, and "
            "order inside a group does not matter. A word is always a rearrangement "
            "of itself, so every word appears in exactly one group."
        ),
        examples=[
            {
                "input": 'words = ["tap", "pat", "top", "pot", "bat"]',
                "output": '[["tap", "pat"], ["top", "pot"], ["bat"]]',
                "explanation": "Each group shares one multiset of letters.",
            }
        ],
        constraints=[
            "There are at most 10000 words.",
            "Each word has length at most 100.",
        ],
        nudge=(
            "Two words belong together when they contain the same letters with the "
            "same counts. What short signature would be identical for every word in "
            "a group and different for the others?"
        ),
        approach=(
            "Use the signature as a map key and append each word to the list stored "
            "there. Sorting the letters works. A count of the 26 letters also works "
            "and avoids sorting each word. Either signature is a valid key."
        ),
        pseudocode=(
            "groups = empty map from signature to list of words\n"
            "for each word:\n"
            "    signature = letters sorted, or a 26-count of letters\n"
            "    append word to groups[signature]\n"
            "return the lists stored in the map"
        ),
        patterns=["canonical key"],
        target_time="O(n)",
        target_space="O(n)",
        acceptable_time=["O(n)", "O(n log n)"],
        complexity_note=(
            "A count signature is linear in the total number of characters. "
            "Sorting each word adds a log factor the checker may report separately."
        ),
        aliases=["group-anagrams"],
    ),
    problem(
        id="longest-consecutive-run",
        title="Longest Consecutive Run",
        topic="hashing",
        tags=["hash-set", "array"],
        difficulty="medium",
        prompt=(
            "Given an unsorted list of integers, return the length of the longest "
            "run of consecutive values. The values do not have to sit next to each "
            "other in the list. Duplicates do not make a run longer. Aim for a "
            "linear amount of work in the length of the list."
        ),
        examples=[
            {
                "input": "values = [100, 4, 200, 1, 3, 2]",
                "output": "4",
                "explanation": "The run 1, 2, 3, 4 has length 4.",
            }
        ],
        constraints=[
            "The list length is at most 100000.",
            "Values fit in a 32-bit signed integer.",
        ],
        nudge=(
            "Sorting makes consecutive values neighbors, but you were asked for a "
            "linear pass. Once every value is in a set, how do you avoid recounting "
            "the same run from every member?"
        ),
        approach=(
            "Insert every value into a set. Only start a run at a value whose "
            "predecessor is absent. From that start, walk forward while the next "
            "integer is present. Each value is visited a constant number of times "
            "across the whole algorithm."
        ),
        pseudocode=(
            "present = set of all values\n"
            "best = 0\n"
            "for each value x in present:\n"
            "    if x - 1 is also present:\n"
            "        continue\n"
            "    length = 1\n"
            "    while x + length is present:\n"
            "        length += 1\n"
            "    best = max(best, length)\n"
            "return best"
        ),
        patterns=["set membership", "run start"],
        target_time="O(n)",
        target_space="O(n)",
        acceptable_time=["O(n)", "O(n log n)"],
        complexity_note="Sorting also solves it, in O(n log n).",
        aliases=["longest-consecutive-sequence"],
    ),
    problem(
        id="count-subarrays-sum-k",
        title="Count Subarrays That Sum to K",
        topic="hashing",
        tags=["prefix-sum", "hash-map"],
        difficulty="medium",
        prompt=(
            "Given a list of integers, which may be negative, and an integer k, "
            "return how many contiguous subarrays sum to k. A subarray is a "
            "contiguous slice, not an arbitrary subset."
        ),
        examples=[
            {
                "input": "values = [1, 2, -1, 1], k = 3",
                "output": "2",
                "explanation": "[1, 2] and [1, 2, -1, 1] both sum to 3.",
            }
        ],
        constraints=["The list length is at most 20000."],
        nudge=(
            "The sum of a slice is the difference of two prefix sums. If you know "
            "the prefix sum at the current index, which earlier prefix would make "
            "the difference equal k?"
        ),
        approach=(
            "Keep a running prefix sum and a map from a prefix sum to how many "
            "times it has occurred. The empty prefix 0 has occurred once before "
            "you start. At each step, add the number of times you have seen "
            "prefix - k, then record the current prefix."
        ),
        pseudocode=(
            "counts = map with 0 seen once\n"
            "prefix = 0\n"
            "answer = 0\n"
            "for each value x:\n"
            "    prefix += x\n"
            "    answer += counts[prefix - k]\n"
            "    counts[prefix] += 1\n"
            "return answer"
        ),
        patterns=["prefix sum frequencies"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["subarray-sum-equals-k"],
    ),
    problem(
        id="top-k-frequent",
        title="The K Most Frequent Values",
        topic="hashing",
        tags=["hash-map", "bucket-sort"],
        difficulty="medium",
        prompt=(
            "Given a list of integers and a positive integer k, return the k "
            "values that appear most often. If several answers are possible, any "
            "one of them is accepted. The expected linear solution does not sort "
            "the whole list."
        ),
        examples=[
            {
                "input": "values = [4, 4, 1, 1, 1, 2, 2], k = 2",
                "output": "[1, 4]",
                "explanation": "1 appears three times and 4 appears twice.",
            }
        ],
        constraints=[
            "k is at least 1 and at most the number of distinct values.",
            "The list length is at most 100000.",
        ],
        nudge=(
            "Counting frequencies is the easy half. Once you know the counts, do "
            "you really need a comparison sort, or can the count itself be a bucket?"
        ),
        approach=(
            "Count with a map. The largest possible count is the length of the list, "
            "so build a list of buckets indexed by frequency and drop each value "
            "into the bucket for its count. Walk the buckets from the highest "
            "frequency downward until you have k values. A heap of size k is a fine "
            "alternative and costs an extra log factor."
        ),
        pseudocode=(
            "freq = counts of each value\n"
            "buckets = a list of empty lists, one per count from 0 through n\n"
            "for each value and its count:\n"
            "    append value to buckets[count]\n"
            "answer = empty\n"
            "for count from n down to 1:\n"
            "    append values from that bucket until answer has k items\n"
            "return answer"
        ),
        patterns=["frequency buckets"],
        target_time="O(n)",
        target_space="O(n)",
        acceptable_time=["O(n)", "O(n log n)"],
        complexity_note="A heap of the frequencies is O(n log k), which this catalog also accepts.",
        aliases=["top-k-frequent-elements"],
    ),
]
