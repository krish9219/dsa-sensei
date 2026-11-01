from dsa_sensei.problems.define import problem

PROBLEMS = [
    problem(
        id="reverse-chain",
        title="Reverse a Singly Linked Chain",
        topic="linked-lists",
        tags=["linked-list"],
        difficulty="easy",
        prompt=(
            "A node has an integer value and a next pointer. Reverse a singly linked "
            "chain in place and return the new head. The empty chain stays empty. "
            "Use only a constant amount of extra memory."
        ),
        examples=[
            {"input": "chain = 1 -> 2 -> 3 -> 4", "output": "4 -> 3 -> 2 -> 1"},
        ],
        constraints=["The chain has at most 10000 nodes."],
        nudge=(
            "Each node needs its next pointer turned around, but if you overwrite "
            "next too early you lose the rest of the chain. What third reference "
            "lets you walk forward while the links point backward?"
        ),
        approach=(
            "Keep previous, current, and a temporary next. For each node, remember "
            "current.next, point current.next at previous, then step both previous "
            "and current forward. When current becomes empty, previous is the new head."
        ),
        pseudocode=(
            "previous = empty\n"
            "current = head\n"
            "while current is not empty:\n"
            "    nxt = current.next\n"
            "    current.next = previous\n"
            "    previous = current\n"
            "    current = nxt\n"
            "return previous"
        ),
        patterns=["three pointers"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["reverse-linked-list"],
    ),
    problem(
        id="middle-node",
        title="Middle Node of a Chain",
        topic="linked-lists",
        tags=["linked-list", "two-pointers"],
        difficulty="easy",
        prompt=(
            "Return the middle node of a singly linked chain. If there are two "
            "middle nodes because the length is even, return the second one. The "
            "chain is non-empty. A single pass is enough."
        ),
        examples=[
            {"input": "chain = 1 -> 2 -> 3 -> 4 -> 5", "output": "node 3"},
            {"input": "chain = 1 -> 2 -> 3 -> 4", "output": "node 3"},
        ],
        constraints=["The chain has at most 100 nodes."],
        nudge=(
            "If one pointer takes single steps and another takes double steps, "
            "where is the slow pointer when the fast one runs out of chain?"
        ),
        approach=(
            "Advance slow by one node and fast by two. When fast is empty or its "
            "next is empty, slow is on the middle this problem wants, including "
            "the second middle of an even-length chain."
        ),
        pseudocode=(
            "slow = fast = head\n"
            "while fast is not empty and fast.next is not empty:\n"
            "    slow = slow.next\n"
            "    fast = fast.next.next\n"
            "return slow"
        ),
        patterns=["slow and fast pointers"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["middle-of-the-linked-list"],
    ),
    problem(
        id="chain-has-loop",
        title="Does This Chain Loop?",
        topic="linked-lists",
        tags=["linked-list", "two-pointers"],
        difficulty="easy",
        prompt=(
            "A singly linked chain might contain a cycle: some node's next pointer "
            "refers to an earlier node. Return whether a cycle exists. Do not change "
            "the chain, and use only a constant amount of extra memory."
        ),
        examples=[
            {
                "input": "chain = 1 -> 2 -> 3 -> 4, and 4 points back at 2",
                "output": "true",
            },
            {"input": "chain = 1 -> 2 -> 3", "output": "false"},
        ],
        constraints=["The chain has at most 10000 nodes if it does not cycle."],
        nudge=(
            "A pointer that moves slowly and a pointer that moves quickly will meet "
            "inside a loop, and only inside a loop. What does it mean if the fast "
            "pointer falls off the end?"
        ),
        approach=(
            "Move slow one step and fast two steps. If they ever refer to the same "
            "node, a cycle exists. If fast reaches the end, it does not. This is "
            "Floyd's cycle finding, and it needs no set of seen nodes."
        ),
        pseudocode=(
            "slow = fast = head\n"
            "while fast is not empty and fast.next is not empty:\n"
            "    slow = slow.next\n"
            "    fast = fast.next.next\n"
            "    if slow is fast: return true\n"
            "return false"
        ),
        patterns=["floyd cycle"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["linked-list-cycle"],
    ),
    problem(
        id="merge-sorted-chains",
        title="Merge Two Sorted Chains",
        topic="linked-lists",
        tags=["linked-list", "two-pointers"],
        difficulty="easy",
        prompt=(
            "Two singly linked chains are each sorted by ascending value. Merge them "
            "into one sorted chain by rewiring next pointers, and return the new head. "
            "Either input may be empty. Do not allocate a node for every value; a "
            "single dummy head is enough."
        ),
        examples=[
            {
                "input": "a = 1 -> 3 -> 5, b = 2 -> 4",
                "output": "1 -> 2 -> 3 -> 4 -> 5",
            }
        ],
        constraints=["Each chain has at most 100 nodes."],
        nudge=(
            "This is the same choice as merging two sorted arrays: always take the "
            "smaller head. What makes the linked version awkward at the very start?"
        ),
        approach=(
            "Attach a dummy node whose next will become the real head. Keep a tail "
            "pointer on the merged chain. While both inputs remain, append the node "
            "with the smaller value and advance that input. Then attach whichever "
            "chain is left. Return dummy.next."
        ),
        pseudocode=(
            "dummy = a new node\n"
            "tail = dummy\n"
            "while both a and b remain:\n"
            "    if a.val <= b.val: attach a and advance a\n"
            "    else: attach b and advance b\n"
            "    tail = tail.next\n"
            "attach whichever of a or b remains\n"
            "return dummy.next"
        ),
        patterns=["dummy head"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["merge-two-sorted-lists"],
    ),
    problem(
        id="drop-nth-from-tail",
        title="Drop the Nth Node from the Tail",
        topic="linked-lists",
        tags=["linked-list", "two-pointers"],
        difficulty="medium",
        prompt=(
            "Remove the nth node from the end of a singly linked chain and return "
            "the new head. n is counted from the tail, starting at 1, and it is "
            "always valid. Do it in one pass. The head itself might be the node "
            "you remove."
        ),
        examples=[
            {
                "input": "chain = 1 -> 2 -> 3 -> 4 -> 5, n = 2",
                "output": "1 -> 2 -> 3 -> 5",
            }
        ],
        constraints=["The chain has at most 100 nodes.", "n is between 1 and the length."],
        nudge=(
            "If two pointers stay n nodes apart, the front one reaching the end "
            "tells you something about the back one. Where do you want the back "
            "pointer to stand when that happens?"
        ),
        approach=(
            "Use a dummy node before the head so removing the head is the same as "
            "removing any other node. Advance a lead pointer n steps. Then move the "
            "lead and a trailer together until the lead falls off. The trailer is "
            "now just before the node to delete, so skip trailer.next."
        ),
        pseudocode=(
            "dummy.next = head\n"
            "lead = dummy\n"
            "advance lead n steps\n"
            "trailer = dummy\n"
            "while lead.next is not empty:\n"
            "    lead = lead.next\n"
            "    trailer = trailer.next\n"
            "trailer.next = trailer.next.next\n"
            "return dummy.next"
        ),
        patterns=["gap of n"],
        target_time="O(n)",
        target_space="O(1)",
        aliases=["remove-nth-from-end"],
    ),
]
