"""Reference solutions used only by tests.

These are not part of the tutor. The CLI and MCP server never import this module.
"""

from __future__ import annotations

SOLUTIONS: dict[str, str] = {
    "pair-with-target": """
def pair(nums, target):
    seen = {}
    for i, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], i]
        seen[value] = i
    return []
""",
    "cluster-scrambles": """
def cluster(words):
    groups = {}
    for word in words:
        counts = [0] * 26
        for ch in word:
            counts[ord(ch) - 97] += 1
        key = tuple(counts)
        groups.setdefault(key, []).append(word)
    return list(groups.values())
""",
    "longest-consecutive-run": """
def longest(nums):
    present = set(nums)
    best = 0
    for value in present:
        if value - 1 in present:
            continue
        length = 1
        while value + length in present:
            length += 1
        best = max(best, length)
    return best
""",
    "count-subarrays-sum-k": """
def count(nums, k):
    seen = {0: 1}
    prefix = answer = 0
    for value in nums:
        prefix += value
        answer += seen.get(prefix - k, 0)
        seen[prefix] = seen.get(prefix, 0) + 1
    return answer
""",
    "top-k-frequent": """
def top_k(nums, k):
    freq = {}
    for value in nums:
        freq[value] = freq.get(value, 0) + 1
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, count in freq.items():
        buckets[count].append(value)
    answer = []
    for count in range(len(buckets) - 1, 0, -1):
        for value in buckets[count]:
            answer.append(value)
            if len(answer) == k:
                return answer
    return answer
""",
    "best-contiguous-sum": """
def best(nums):
    ending = best_sum = nums[0]
    for value in nums[1:]:
        ending = value if value > ending + value else ending + value
        if ending > best_sum:
            best_sum = ending
    return best_sum
""",
    "product-of-others": """
def products(nums):
    n = len(nums)
    out = [1] * n
    running = 1
    for i in range(n):
        out[i] = running
        running *= nums[i]
    running = 1
    for i in range(n - 1, -1, -1):
        out[i] *= running
        running *= nums[i]
    return out
""",
    "rotate-right": """
def rotate(nums, k):
    n = len(nums)
    k %= n
    def rev(i, j):
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j -= 1
    rev(0, n - 1)
    rev(0, k - 1)
    rev(k, n - 1)
""",
    "merge-sorted-arrays": """
def merge(left, right):
    i = j = 0
    out = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
""",
    "dominating-value": """
def majority(nums):
    candidate = 0
    count = 0
    for value in nums:
        if count == 0:
            candidate = value
        count += 1 if value == candidate else -1
    return candidate
""",
    "sorted-pair-sum": """
def pair(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        total = nums[lo] + nums[hi]
        if total == target:
            return [lo, hi]
        if total < target:
            lo += 1
        else:
            hi -= 1
    return []
""",
    "phrase-palindrome": """
def is_phrase(text):
    lo, hi = 0, len(text) - 1
    while lo < hi:
        while lo < hi and not text[lo].isalnum():
            lo += 1
        while lo < hi and not text[hi].isalnum():
            hi -= 1
        if text[lo].lower() != text[hi].lower():
            return False
        lo += 1
        hi -= 1
    return True
""",
    "widest-pool": """
def pool(heights):
    lo, hi = 0, len(heights) - 1
    best = 0
    while lo < hi:
        width = hi - lo
        limit = heights[lo] if heights[lo] < heights[hi] else heights[hi]
        area = width * limit
        if area > best:
            best = area
        if heights[lo] <= heights[hi]:
            lo += 1
        else:
            hi -= 1
    return best
""",
    "zero-sum-triplets": """
def triplets(nums):
    nums = sorted(nums)
    found = []
    for i in range(len(nums)):
        if i and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            total = nums[i] + nums[lo] + nums[hi]
            if total == 0:
                found.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
            elif total < 0:
                lo += 1
            else:
                hi -= 1
    return found
""",
    "trapped-rain": """
def trap(heights):
    lo, hi = 0, len(heights) - 1
    left_max = right_max = water = 0
    while lo < hi:
        if heights[lo] <= heights[hi]:
            left_max = heights[lo] if heights[lo] > left_max else left_max
            water += left_max - heights[lo]
            lo += 1
        else:
            right_max = heights[hi] if heights[hi] > right_max else right_max
            water += right_max - heights[hi]
            hi -= 1
    return water
""",
    "push-zeroes-back": """
def push(nums):
    write = 0
    for value in nums:
        if value != 0:
            nums[write] = value
            write += 1
    for i in range(write, len(nums)):
        nums[i] = 0
""",
    "fixed-window-best-sum": """
def best(nums, k):
    window = sum(nums[:k])
    best_sum = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]
        if window > best_sum:
            best_sum = window
    return best_sum
""",
    "longest-unique-stretch": """
def longest(text):
    left = best = 0
    counts = {}
    for right, ch in enumerate(text):
        counts[ch] = counts.get(ch, 0) + 1
        while counts[ch] > 1:
            counts[text[left]] -= 1
            left += 1
        span = right - left + 1
        if span > best:
            best = span
    return best
""",
    "shortest-covering-window": """
def cover(source, need):
    required = {}
    for ch in need:
        required[ch] = required.get(ch, 0) + 1
    missing = len(required)
    have = {}
    left = 0
    best_len = len(source) + 1
    best_at = 0
    for right, ch in enumerate(source):
        have[ch] = have.get(ch, 0) + 1
        if ch in required and have[ch] == required[ch]:
            missing -= 1
        while missing == 0:
            span = right - left + 1
            if span < best_len:
                best_len = span
                best_at = left
            drop = source[left]
            have[drop] -= 1
            if drop in required and have[drop] < required[drop]:
                missing += 1
            left += 1
    if best_len > len(source):
        return ""
    return source[best_at : best_at + best_len]
""",
    "rearrangement-window": """
def has_perm(source, pattern):
    if len(pattern) > len(source):
        return False
    need = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    window = {}
    for ch in source[: len(pattern)]:
        window[ch] = window.get(ch, 0) + 1
    if window == need:
        return True
    for right in range(len(pattern), len(source)):
        enter = source[right]
        leave = source[right - len(pattern)]
        window[enter] = window.get(enter, 0) + 1
        window[leave] -= 1
        if window[leave] == 0:
            del window[leave]
        if window == need:
            return True
    return False
""",
    "sorted-lookup": """
def lookup(nums, target):
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
""",
    "insertion-index": """
def insert_at(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
""",
    "rotated-lookup": """
def lookup(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        elif nums[mid] < target <= nums[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""",
    "rotated-minimum": """
def minimum(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
""",
    "lightest-ship": """
def ship(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        needed = 1
        load = 0
        for weight in weights:
            if load + weight > mid:
                needed += 1
                load = 0
            load += weight
        if needed <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    "median-two-sorted": """
def median(left, right):
    if len(left) > len(right):
        left, right = right, left
    total = len(left) + len(right)
    half = total // 2
    lo, hi = 0, len(left)
    while lo <= hi:
        cut_left = lo + (hi - lo) // 2
        cut_right = half - cut_left
        left_max = left[cut_left - 1] if cut_left else float("-inf")
        left_min = left[cut_left] if cut_left < len(left) else float("inf")
        right_max = right[cut_right - 1] if cut_right else float("-inf")
        right_min = right[cut_right] if cut_right < len(right) else float("inf")
        if left_max <= right_min and right_max <= left_min:
            if total % 2:
                return left_min if left_min < right_min else right_min
            high = left_max if left_max > right_max else right_max
            low = left_min if left_min < right_min else right_min
            return (high + low) / 2
        if left_max > right_min:
            hi = cut_left - 1
        else:
            lo = cut_left + 1
    return 0.0
""",
    "reverse-chain": """
def reverse(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev
""",
    "middle-node": """
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
""",
    "chain-has-loop": """
def has_loop(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
""",
    "merge-sorted-chains": """
def merge(a, b):
    dummy = Node(0)
    tail = dummy
    while a and b:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
""",
    "drop-nth-from-tail": """
def drop(head, n):
    dummy = Node(0)
    dummy.next = head
    lead = dummy
    for _ in range(n):
        lead = lead.next
    trail = dummy
    while lead.next:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return dummy.next
""",
    "balanced-brackets": """
def balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack[-1] != pairs[ch]:
            return False
        else:
            stack.pop()
    return not stack
""",
    "min-tracking-stack": """
class MinStack:
    def __init__(self):
        self._data = []
    def push(self, value):
        current = value if not self._data else min(value, self._data[-1][1])
        self._data.append((value, current))
    def pop(self):
        self._data.pop()
    def top(self):
        return self._data[-1][0]
    def get_min(self):
        return self._data[-1][1]
""",
    "wait-for-warmer": """
def wait(temps):
    answer = [0] * len(temps)
    stack = []
    for i, temp in enumerate(temps):
        while stack and temps[stack[-1]] < temp:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer
""",
    "postfix-eval": """
def evaluate(tokens):
    stack = []
    for token in tokens:
        if token not in {"+", "-", "*", "/"}:
            stack.append(int(token))
            continue
        right = stack.pop()
        left = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            stack.append(int(left / right))
    return stack[-1]
""",
    "histogram-largest": """
def largest(heights):
    best = 0
    stack = [-1]
    bars = list(heights) + [0]
    for i, height in enumerate(bars):
        while stack[-1] != -1 and heights[stack[-1]] > height:
            h = heights[stack.pop()]
            width = i - stack[-1] - 1
            area = h * width
            if area > best:
                best = area
        stack.append(i)
    return best
""",
    "tree-depth": """
def depth(node):
    if not node:
        return 0
    left = depth(node.left)
    right = depth(node.right)
    return 1 + (left if left > right else right)
""",
    "mirror-tree": """
def mirror(node):
    if not node:
        return None
    node.left, node.right = mirror(node.right), mirror(node.left)
    return node
""",
    "identical-trees": """
def same(p, q):
    if not p or not q:
        return p is q
    return p.val == q.val and same(p.left, q.left) and same(p.right, q.right)
""",
    "levels-of-tree": """
from collections import deque
def levels(root):
    if not root:
        return []
    queue = deque([root])
    out = []
    while queue:
        layer = []
        width = len(queue)
        for _ in range(width):
            node = queue.popleft()
            layer.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        out.append(layer)
    return out
""",
    "search-tree-check": """
def valid(node, low, high):
    if not node:
        return True
    if node.val <= low or node.val >= high:
        return False
    return valid(node.left, low, node.val) and valid(node.right, node.val, high)
""",
    "shared-ancestor": """
def lca(node, p, q):
    if not node or node is p or node is q:
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left and right:
        return node
    return left or right
""",
    "count-islands": """
from collections import deque
def islands(grid):
    if not grid:
        return 0
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != "1":
                continue
            count += 1
            queue = deque([(r, c)])
            grid[r][c] = "0"
            while queue:
                x, y = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = x + dr, y + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == "1":
                        grid[nr][nc] = "0"
                        queue.append((nr, nc))
    return count
""",
    "course-schedule-order": """
def order(n, prereqs):
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for course, pre in prereqs:
        graph[pre].append(course)
        indegree[course] += 1
    queue = [i for i in range(n) if indegree[i] == 0]
    result = []
    while queue:
        node = queue.pop()
        result.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return result if len(result) == n else []
""",
    "copy-graph": """
def copy(node):
    if node is None:
        return None
    clones = {node: Node(node.val)}
    stack = [node]
    while stack:
        current = stack.pop()
        for nei in current.neighbors:
            if nei not in clones:
                clones[nei] = Node(nei.val)
                stack.append(nei)
            clones[current].neighbors.append(clones[nei])
    return clones[node]
""",
    "stair-ways": """
def ways(n):
    if n <= 2:
        return n
    prev, curr = 1, 2
    for _ in range(n - 2):
        prev, curr = curr, prev + curr
    return curr
""",
    "street-loot": """
def loot(houses):
    take = skip = 0
    for amount in houses:
        take, skip = amount + skip, take if take > skip else skip
    return take if take > skip else skip
""",
    "fewest-coins": """
def coins_for(coins, amount):
    dp = [0] + [amount + 1] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and dp[value - coin] + 1 < dp[value]:
                dp[value] = dp[value - coin] + 1
    return dp[amount] if dp[amount] <= amount else -1
""",
    "longest-rising-subsequence": """
import bisect
def length(nums):
    tails = []
    for value in nums:
        index = bisect.bisect_left(tails, value)
        if index == len(tails):
            tails.append(value)
        else:
            tails[index] = value
    return len(tails)
""",
    "edit-distance": """
def edits(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                best = dp[i - 1][j]
                if dp[i][j - 1] < best:
                    best = dp[i][j - 1]
                if dp[i - 1][j - 1] < best:
                    best = dp[i - 1][j - 1]
                dp[i][j] = best + 1
    return dp[len(a)][len(b)]
""",
}
