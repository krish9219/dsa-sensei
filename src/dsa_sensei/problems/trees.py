from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="tree-depth",
        title="Depth of a Binary Tree",
        topic="trees",
        tags=["tree", "dfs"],
        difficulty="easy",
        prompt=(
            "A binary tree node has a value, a left child, and a right child. The "
            "depth of an empty tree is 0. The depth of any other tree is 1 plus the "
            "depth of its deeper child. Return the depth of the root."
        ),
        examples=[
            {
                "input": "root = 1, with left 2 and right 3, and 2 has a left child 4",
                "output": "3",
            }
        ],
        constraints=["The tree has at most 10000 nodes."],
        nudge=(
            "The answer at a node is completely determined by the answers at its "
            "two children. What is the base case when the node itself is missing?"
        ),
        approach=(
            "Recurse. An empty child contributes 0. A real node contributes 1 plus "
            "the larger of the two recursive results. An iterative version can count "
            "levels with a queue, but the recursive form matches the definition directly."
        ),
        pseudocode=(
            "depth(node):\n"
            "    if node is empty: return 0\n"
            "    return 1 + max(depth(node.left), depth(node.right))"
        ),
        patterns=["tree recursion"],
        target_time="O(n)",
        target_space="O(n)",
        complexity_note=(
            "Time is linear in the number of nodes. Extra space is the recursion depth, "
            "which is n in a skewed tree."
        ),
        aliases=["maximum-depth-of-binary-tree"],
    ),
    problem(
        id="mirror-tree",
        title="Mirror a Binary Tree",
        topic="trees",
        tags=["tree", "dfs"],
        difficulty="easy",
        prompt=(
            "Swap the left and right child of every node in a binary tree, all the "
            "way down, and return the root. The mirror of an empty tree is empty."
        ),
        examples=[
            {
                "input": "root 1 with left 2 and right 3",
                "output": "root 1 with left 3 and right 2",
            }
        ],
        constraints=["The tree has at most 100 nodes."],
        nudge=(
            "Swapping only the root's children leaves the subtrees facing the "
            "original way. What has to happen to each subtree before or after the swap?"
        ),
        approach=(
            "At each node, recursively mirror the left subtree and the right subtree, "
            "then exchange the two child pointers. The order of swapping and recurring "
            "does not matter as long as both subtrees are mirrored and the pointers move."
        ),
        pseudocode=(
            "mirror(node):\n"
            "    if node is empty: return empty\n"
            "    mirror(node.left)\n"
            "    mirror(node.right)\n"
            "    swap node.left and node.right\n"
            "    return node"
        ),
        patterns=["tree recursion"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["invert-binary-tree"],
    ),
    problem(
        id="identical-trees",
        title="Are Two Binary Trees Identical?",
        topic="trees",
        tags=["tree", "dfs"],
        difficulty="easy",
        prompt=(
            "Two binary trees are identical when they have the same shape and the "
            "same values in the same positions. Return whether two roots describe "
            "identical trees. Two empty trees are identical."
        ),
        examples=[
            {
                "input": "p = 1 with children 2 and 3; q = 1 with children 2 and 3",
                "output": "true",
            },
            {
                "input": "p = 1 with left 2; q = 1 with right 2",
                "output": "false",
            },
        ],
        constraints=["Each tree has at most 100 nodes."],
        nudge=(
            "A mismatch is either two different values or one side being empty "
            "while the other is not. If the roots agree, what else has to agree?"
        ),
        approach=(
            "If both nodes are empty, they match. If only one is empty, or the "
            "values differ, they do not. Otherwise both left subtrees must match "
            "and both right subtrees must match."
        ),
        pseudocode=(
            "same(p, q):\n"
            "    if both are empty: return true\n"
            "    if one is empty or p.val != q.val: return false\n"
            "    return same(p.left, q.left) and same(p.right, q.right)"
        ),
        patterns=["simultaneous recursion"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["same-tree"],
    ),
    problem(
        id="levels-of-tree",
        title="Visit a Tree Level by Level",
        topic="trees",
        tags=["tree", "bfs"],
        difficulty="medium",
        prompt=(
            "Return the values of a binary tree as a list of levels, from the root "
            "downward, each level from left to right. The empty tree yields an empty list."
        ),
        examples=[
            {
                "input": "root 1, left 2 with child 4, right 3",
                "output": "[[1], [2, 3], [4]]",
            }
        ],
        constraints=["The tree has at most 2000 nodes."],
        nudge=(
            "A stack would dive to the bottom. You want every node at the current "
            "distance before any node that is farther. Which structure visits nodes "
            "in the order they were discovered?"
        ),
        approach=(
            "Use a queue, starting with the root. While the queue is not empty, "
            "record how many nodes it currently holds: that many belong to this "
            "level. Pop each of them, append their value, and push their existing "
            "children. Start the next level with whatever was just pushed."
        ),
        pseudocode=(
            "if root is empty: return []\n"
            "queue = [root]\n"
            "levels = []\n"
            "while queue is not empty:\n"
            "    this level has the current length of the queue\n"
            "    pop that many nodes, record values, push children\n"
            "    append the level\n"
            "return levels"
        ),
        patterns=["breadth-first search"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["binary-tree-level-order"],
    ),
    problem(
        id="search-tree-check",
        title="Is This a Binary Search Tree?",
        topic="trees",
        tags=["tree", "bst"],
        difficulty="medium",
        prompt=(
            "A binary search tree requires every node to be strictly greater than "
            "every value in its left subtree and strictly less than every value in "
            "its right subtree. Duplicates are not allowed. Return whether a binary "
            "tree satisfies that rule. An empty tree does."
        ),
        examples=[
            {
                "input": "root 5, left 3, right 8, and 3 has children 1 and 4",
                "output": "true",
            },
            {
                "input": "root 5, left 6, right 8",
                "output": "false",
            },
        ],
        constraints=["The tree has at most 10000 nodes."],
        nudge=(
            "Comparing a node only with its parent is not enough. A value deep on "
            "the left can still be larger than an ancestor. What range is a node "
            "allowed to occupy?"
        ),
        approach=(
            "Carry an open lower bound and an open upper bound down the recursion. "
            "The root may be anything. A left child must be below the current node "
            "and still above the inherited lower bound; a right child must be above "
            "the current node and below the inherited upper bound. Reject a node "
            "that falls outside its range."
        ),
        pseudocode=(
            "valid(node, low, high):\n"
            "    if node is empty: return true\n"
            "    if node.val <= low or node.val >= high: return false\n"
            "    return valid(node.left, low, node.val)\n"
            "       and valid(node.right, node.val, high)\n"
            "start with low = -infinity and high = +infinity"
        ),
        patterns=["bounds down the tree"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["validate-binary-search-tree"],
    ),
    problem(
        id="shared-ancestor",
        title="Lowest Shared Ancestor",
        topic="trees",
        tags=["tree", "dfs"],
        difficulty="medium",
        prompt=(
            "In a binary tree that is not necessarily a search tree, two distinct "
            "nodes p and q both exist. Return the lowest node that has both p and q "
            "in its subtree. A node counts as being in its own subtree, so if one "
            "node is an ancestor of the other, that ancestor is the answer."
        ),
        examples=[
            {
                "input": "root 3, left 5, right 1; 5 has children 6 and 2; p = 6, q = 1",
                "output": "3",
            }
        ],
        constraints=["The tree has between 2 and 100000 nodes.", "p and q are present."],
        nudge=(
            "Ask each subtree whether it contains p, q, both, or neither. If the "
            "two sides of a node disagree about which target they found, what does "
            "that say about the node you are standing on?"
        ),
        approach=(
            "Search post-order. If a subtree returns a node, it found p, q, or their "
            "ancestor. If the current node is p or q, return it immediately, even if "
            "the other target is below it: the current node is then the ancestor. If "
            "the left and right searches both return a node, the current node is the "
            "split point. If only one side returns a node, pass that result upward."
        ),
        pseudocode=(
            "lca(node):\n"
            "    if node is empty or node is p or node is q: return node\n"
            "    left = lca(node.left)\n"
            "    right = lca(node.right)\n"
            "    if both left and right are found: return node\n"
            "    return whichever of left or right was found"
        ),
        patterns=["post-order split"],
        target_time="O(n)",
        target_space="O(n)",
        aliases=["lowest-common-ancestor"],
    ),
]
