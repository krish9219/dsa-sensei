from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="balanced-brackets",
        title="Balanced Brackets",
        topic="stacks",
        tags=["stack", "string"],
        difficulty="easy",
        prompt=(
            "A string contains only the brackets ()[]{}. It is balanced when every "
            "opener has the matching closer, closers never appear too early, and "
            "nothing is left open at the end. Return whether the string is balanced. "
            "The empty string is balanced."
        ),
        examples=[
            {"input": 'text = "()[]{}"', "output": "true"},
            {"input": 'text = "([)]"', "output": "false"},
            {"input": 'text = "((("', "output": "false"},
        ],
        constraints=["The string length is at most 10000."],
        nudge=(
            "The closer you are allowed to see next is exactly the most recent "
            "opener that is still unmatched. What structure gives you that opener?"
        ),
        approach=(
            "Push opening brackets. On a closer, the stack must be non-empty and "
            "its top must be the matching opener; then pop. At the end the stack "
            "must be empty. A map from closer to opener keeps the cases in one place."
        ),
        pseudocode=(
            "pairs = map each closer to its opener\n"
            "stack = empty\n"
            "for each character ch:\n"
            "    if ch is an opener: push it\n"
            "    else if stack is empty or stack top is not pairs[ch]: return false\n"
            "    else: pop\n"
            "return whether the stack is empty"
        ),
        patterns=["stack of openers"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["valid-parentheses"],
    ),
    problem(
        id="min-tracking-stack",
        title="Stack That Remembers Its Minimum",
        topic="stacks",
        tags=["stack", "design"],
        difficulty="medium",
        prompt=(
            "Design a stack of integers with push, pop, top, and get_min. Each "
            "operation should run in constant time. get_min returns the smallest "
            "value currently stored. pop and top are only called when the stack "
            "is not empty. There may be duplicate values."
        ),
        examples=[
            {
                "input": "push 3, push 1, get_min, push 1, pop, get_min",
                "output": "1, then 1",
                "explanation": "After popping the second 1, the minimum is still 1.",
            }
        ],
        constraints=["There will be at most 10000 operations."],
        nudge=(
            "The minimum only changes when you push something smaller or pop the "
            "value that currently defines it. How can each stored item remember "
            "the minimum that was in force when it was pushed?"
        ),
        approach=(
            "Store pairs, or use a second stack of minima. On push, the minimum "
            "becomes the smaller of the new value and the previous minimum. On pop, "
            "throwing away that record restores the previous minimum automatically. "
            "top reads the value half of the pair. All four operations are O(1)."
        ),
        pseudocode=(
            "stack stores pairs (value, min_so_far)\n"
            "push(x):\n"
            "    current_min = x if stack is empty else min(x, stack.top.min)\n"
            "    push (x, current_min)\n"
            "pop: pop the pair\n"
            "top: return the value of the top pair\n"
            "get_min: return the min of the top pair"
        ),
        patterns=["augmented stack"],
        target_time="O(1)",
        target_space="O(n)",
        complexity_note="Each operation is O(1). The structure uses linear memory in the number of pushes.",
        aliases=["min-stack"],
    ),
    problem(
        id="wait-for-warmer",
        title="Days Until a Warmer Temperature",
        topic="stacks",
        tags=["stack", "monotonic-stack"],
        difficulty="medium",
        prompt=(
            "temps[i] is the temperature on day i. For each day, return how many "
            "days you wait until a strictly warmer temperature. If no warmer day "
            "comes, the answer for that day is 0."
        ),
        examples=[
            {
                "input": "temps = [73, 74, 75, 71, 69, 72, 76, 73]",
                "output": "[1, 1, 4, 2, 1, 1, 0, 0]",
            }
        ],
        constraints=["There is at least one day and at most 100000."],
        nudge=(
            "A colder day cannot be the answer for anyone while a warmer unresolved "
            "day is still waiting. Which earlier days can you discard the moment "
            "you see a new temperature?"
        ),
        approach=(
            "Keep a stack of indices whose temperatures are still waiting for a "
            "warmer day, stored so the temperatures increase toward the bottom. "
            "When today's temperature is warmer than the stack's top, that top has "
            "found its answer: the distance in days. Pop until the stack is warmer "
            "again, then push today. Each index is pushed and popped at most once."
        ),
        pseudocode=(
            "answer = zeros of length n\n"
            "stack = empty list of indices\n"
            "for i, temperature in temps:\n"
            "    while stack is not empty and temps[stack.top] < temperature:\n"
            "        j = pop stack\n"
            "        answer[j] = i - j\n"
            "    push i\n"
            "return answer"
        ),
        patterns=["monotonic stack"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["daily-temperatures"],
    ),
    problem(
        id="postfix-eval",
        title="Evaluate a Postfix Expression",
        topic="stacks",
        tags=["stack", "math"],
        difficulty="medium",
        prompt=(
            "Tokens are either integers or one of the operators +, -, *, /. The "
            "expression is written in postfix: an operator comes after its two "
            "operands. Evaluate it. Division truncates toward zero. Every operator "
            "has two operands available, and the expression is non-empty."
        ),
        examples=[
            {"input": 'tokens = ["2", "1", "+", "3", "*"]', "output": "9"},
            {"input": 'tokens = ["4", "13", "5", "/", "+"]', "output": "6"},
        ],
        constraints=["There are at most 10000 tokens.", "Division by zero does not occur."],
        nudge=(
            "An operator always applies to the two most recent values that are "
            "still unused. Where should those values wait?"
        ),
        approach=(
            "Push integers onto a stack. When you see an operator, pop the right "
            "operand first and then the left, apply the operator, and push the "
            "result. Toward-zero division is not the same as floor division for "
            "negatives, so truncate explicitly. The stack's only item at the end "
            "is the answer."
        ),
        pseudocode=(
            "stack = empty\n"
            "for each token:\n"
            "    if token is a number: push it\n"
            "    else:\n"
            "        right = pop, left = pop\n"
            "        push left <op> right, with division truncated toward zero\n"
            "return the last value"
        ),
        patterns=["operand stack"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["evaluate-reverse-polish-notation", "rpn"],
    ),
    problem(
        id="histogram-largest",
        title="Largest Rectangle in a Histogram",
        topic="stacks",
        tags=["stack", "monotonic-stack"],
        difficulty="hard",
        prompt=(
            "Each integer is the height of a bar of width 1 in a histogram. Return "
            "the area of the largest rectangle that fits under the skyline. The "
            "rectangle's sides must sit on bar boundaries, and its height is limited "
            "by the shortest bar it covers."
        ),
        examples=[
            {
                "input": "heights = [3, 1, 3, 2, 2]",
                "output": "6",
                "explanation": "A height of 2 covers the last three bars.",
            }
        ],
        constraints=["There is at least one bar and at most 100000."],
        nudge=(
            "For each bar, the largest rectangle that uses it as the shortest bar "
            "extends left and right until a strictly shorter bar. How can a stack "
            "tell you both boundaries when you finally see a shorter bar?"
        ),
        approach=(
            "Keep a stack of bar indices in increasing height. When the next bar is "
            "shorter than the stack's top, the top bar's rectangle ends here. Its "
            "height is that bar, and its left boundary is the new top of the stack "
            "(or the start, if the stack is empty). Pop and record the area, then "
            "continue. A sentinel of height 0 at the end flushes the stack."
        ),
        pseudocode=(
            "best = 0\n"
            "stack = [-1]\n"
            "consider every bar, plus a final height of 0\n"
            "while the bar under the stack top is taller than the current height:\n"
            "    h = height at the popped index\n"
            "    width = current index - stack top - 1\n"
            "    best = max(best, h * width)\n"
            "push the current index\n"
            "return best"
        ),
        patterns=["nearest smaller bars"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["largest-rectangle-in-histogram"],
    ),
]
