from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="count-islands",
        title="Count the Islands",
        topic="graphs",
        tags=["graph", "dfs", "grid"],
        difficulty="medium",
        prompt=(
            "A grid of characters '1' and '0' is a map of land and water. An island "
            "is a group of land cells connected by edges, not by corners. Return how "
            "many islands the map contains. You may overwrite cells to mark them visited."
        ),
        examples=[
            {
                "input": 'grid = [["1","1","0"],["0","1","0"],["0","0","1"]]',
                "output": "2",
            }
        ],
        constraints=[
            "The grid has at most 300 rows and 300 columns.",
            "It may be empty.",
        ],
        nudge=(
            "Every land cell belongs to exactly one island. Once you find a land "
            "cell you have not counted, how do you make sure the rest of that island "
            "is not counted again?"
        ),
        approach=(
            "Scan every cell. When you see land, increment the island count and "
            "flood-fill the connected land, marking cells as water or visited as "
            "you go. Depth-first or breadth-first search both work. Each cell is "
            "entered a constant number of times, so the work is proportional to the "
            "number of cells."
        ),
        pseudocode=(
            "count = 0\n"
            "for each cell:\n"
            "    if the cell is land:\n"
            "        count += 1\n"
            "        flood-fill its four-direction neighbors, marking them visited\n"
            "return count"
        ),
        patterns=["flood fill"],
        target_time="O(n)",
        target_space="O(n)",
        complexity_note=(
            "n is the number of cells. A recursive fill uses stack space proportional to the island."
        ),
        aliases=["number-of-islands"],
    ),
    problem(
        id="course-schedule-order",
        title="An Order That Respects Prerequisites",
        topic="graphs",
        tags=["graph", "topological-sort"],
        difficulty="medium",
        prompt=(
            "There are n courses labeled 0 through n - 1. You are given pairs "
            "[course, prerequisite] meaning the prerequisite must be finished before "
            "the course. Return any order in which all courses can be taken. If the "
            "requirements contain a cycle, return an empty list."
        ),
        examples=[
            {
                "input": "n = 4, prereqs = [[1, 0], [2, 0], [3, 1], [3, 2]]",
                "output": "[0, 1, 2, 3]",
                "explanation": "[0, 2, 1, 3] is also valid.",
            }
        ],
        constraints=["n is at most 2000.", "There are at most 5000 prerequisite pairs."],
        nudge=(
            "A course can be taken when nothing it depends on is still unfinished. "
            "Which courses are legal on day one, and what happens to the others "
            "after you take one?"
        ),
        approach=(
            "Build a graph from prerequisite to the courses it unlocks, and count "
            "how many unmet prerequisites each course has. Put every course with "
            "count zero into a queue. Pop a course into the answer and decrement "
            "the count of each course it unlocks. Newly zero counts join the queue. "
            "If the answer is shorter than n, some courses were trapped in a cycle."
        ),
        pseudocode=(
            "unlocks = adjacency lists\n"
            "indegree = counts\n"
            "queue = every course with indegree 0\n"
            "order = empty\n"
            "while queue is not empty:\n"
            "    take course c\n"
            "    append c to order\n"
            "    for each course it unlocks:\n"
            "        decrease indegree, and enqueue it if the count hits 0\n"
            "return order if its length is n, else []"
        ),
        patterns=["kahn topological sort"],
        target_time="O(n + e)",
        target_space="O(n + e)",
        aliases=["course-schedule-ii"],
    ),
    problem(
        id="copy-graph",
        title="Deep Copy an Undirected Graph",
        topic="graphs",
        tags=["graph", "dfs", "hash-map"],
        difficulty="medium",
        prompt=(
            "Each node has an integer value and a list of neighboring nodes. The "
            "graph is connected and undirected. Given one node, return a deep copy: "
            "new node objects, the same connections, and no node shared with the "
            "original. If the input node is missing, return nothing."
        ),
        examples=[
            {
                "input": (
                    "node 1 connected to 2 and 4; 2 connected to 1 and 3; "
                    "3 connected to 2 and 4; 4 connected to 1 and 3"
                ),
                "output": "a new graph with the same shape",
            }
        ],
        constraints=["There are at most 100 nodes.", "Values are unique."],
        nudge=(
            "The graph may contain cycles, so a naive recursion will copy the same "
            "node forever. What do you need to remember the first time you create "
            "a clone of a particular original node?"
        ),
        approach=(
            "Map each original node to its clone. When you first see a node, create "
            "the clone and store it before walking the neighbors. When you see a "
            "node that already has a clone, reuse it. Depth-first and breadth-first "
            "search both work; the map is what stops the cycle."
        ),
        pseudocode=(
            "if start is empty: return empty\n"
            "clones = map from original node to a new node with the same value\n"
            "stack or queue = [start]\n"
            "while nodes remain:\n"
            "    for each neighbor of the current original:\n"
            "        create its clone if needed and remember to visit it\n"
            "        connect the current clone to the neighbor's clone\n"
            "return clones[start]"
        ),
        patterns=["clone map"],
        target_time="O(n + e)",
        target_space="O(n)",
        aliases=["clone-graph"],
    ),
]
