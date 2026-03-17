class BPlusTreeNode:
    """
    Represents a single node in a B+ Tree.

    In a B+ Tree:
      - Internal nodes store only keys and child pointers (no values).
      - Leaf nodes store keys, their associated values, and a `next`
        pointer to form a linked list across all leaves.

    Attributes:
        order      : int  – max number of keys a node can hold (branching factor - 1)
        is_leaf    : bool – True if this is a leaf node
        keys       : list – sorted list of keys
        values     : list – parallel list of values (leaf nodes only; None for internal)
        children   : list – child node pointers (internal nodes only; [] for leaves)
        next       : BPlusTreeNode | None – pointer to next leaf (leaf nodes only)
        parent     : BPlusTreeNode | None – pointer to parent node (optional, useful for deletion)
    """

    def __init__(self, order: int, is_leaf: bool = False):
        """
        Args:
            order  : The order of the B+ Tree (max keys per node = order - 1).
            is_leaf: Whether this node is a leaf node.
        """
        self.order    = order
        self.is_leaf  = is_leaf
        self.keys     = []          # Sorted list of keys

        # Leaf nodes: values[i] is the record associated with keys[i]
        # Internal nodes: values is unused (None)
        self.values   = [] if is_leaf else None

        # Internal nodes: len(children) == len(keys) + 1
        # Leaf nodes: children is unused (empty list)
        self.children = []

        # Leaf-level linked list pointer (leaf nodes only)
        self.next     = None

        # Back-pointer to parent (makes deletion/rebalancing easier)
        self.parent   = None

    # ------------------------------------------------------------------ #
    #  Capacity helpers                                                    #
    # ------------------------------------------------------------------ #

    def is_full(self) -> bool:
        """Returns True if the node has reached maximum key capacity."""
        return len(self.keys) >= self.order - 1

    def is_underflow(self) -> bool:
        """
        Returns True if the node has fewer than the minimum required keys.
        Minimum keys = ceil(order / 2) - 1  (root is exempt).
        """
        import math
        return len(self.keys) < math.ceil(self.order / 2) - 1

    def has_excess(self) -> bool:
        """
        Returns True if the node can lend a key to a sibling during
        redistribution (has more than the minimum required keys).
        """
        import math
        return len(self.keys) > math.ceil(self.order / 2) - 1

    # ------------------------------------------------------------------ #
    #  Search helper                                                       #
    # ------------------------------------------------------------------ #

    def find_child_index(self, key) -> int:
        """
        For an internal node, returns the index i such that
        children[i] is the correct subtree to descend into for `key`.

        Uses linear scan; works for small orders.
        For large orders, replace with bisect.bisect_left for O(log n).
        """
        i = 0
        while i < len(self.keys) and key >= self.keys[i]:
            i += 1
        return i

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        kind = "Leaf" if self.is_leaf else "Internal"
        return f"BPlusTreeNode({kind}, keys={self.keys})"
    
import math
from database.bplustree_node import BPlusTreeNode  # adjust import as needed

class BPlusTree:
    """
    A B+ Tree implementation supporting insert, delete, search,
    range queries, update, and Graphviz visualisation.

    Properties:
        - All data lives in leaf nodes only.
        - Internal nodes hold keys as routing separators.
        - Leaf nodes are linked via `next` pointers for efficient range scans.
        - Nodes split when full (on insert) and merge/redistribute on underflow (on delete).

    Args:
        order : int – max children per internal node (min 3).
                      Max keys per node = order - 1.
                      Min keys per node = ceil(order / 2) - 1.
    """

    def __init__(self, order: int = 4):
        if order < 3:
            raise ValueError("Order must be at least 3.")
        self.order = order
        self.root  = BPlusTreeNode(order=order, is_leaf=True)
        self._min_keys = math.ceil(order / 2) - 1

    # ================================================================== #
    #  SEARCH                                                              #
    # ================================================================== #

    def search(self, key):
        """
        Search for a key. Returns associated value if found, else None.
        Traverses from root down to the correct leaf node.
        Time complexity: O(log n)
        """
        leaf = self._find_leaf(key)
        if key in leaf.keys:
            return leaf.values[leaf.keys.index(key)]
        return None

    def _find_leaf(self, key) -> BPlusTreeNode:
        """Traverse from root to the leaf node where `key` belongs."""
        node = self.root
        while not node.is_leaf:
            i = node.find_child_index(key)
            node = node.children[i]
        return node

    # ================================================================== #
    #  INSERT                                                              #
    # ================================================================== #

    def insert(self, key, value):
        """
        Insert a key-value pair into the B+ Tree.
        - If key already exists, update its value (no duplicates).
        - Splits nodes bottom-up when full.
        Time complexity: O(log n)
        """
        # If key exists, just update
        if self.search(key) is not None:
            self.update(key, value)
            return

        self._insert_non_full(self.root, key, value)

        # If root is now full after insertion, split it
        if len(self.root.keys) >= self.order:
            old_root  = self.root
            new_root  = BPlusTreeNode(order=self.order, is_leaf=False)
            self.root = new_root
            new_root.children.append(old_root)
            old_root.parent = new_root
            self._split_child(new_root, 0)

    def _insert_non_full(self, node: BPlusTreeNode, key, value):
        """
        Recursively descend to the correct leaf and insert.
        Splits children proactively if they are full before descending.
        """
        if node.is_leaf:
            # Insert key in sorted position
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            i = node.find_child_index(key)
            child = node.children[i]

            # Pre-emptively split a full child before descending
            if len(child.keys) >= self.order - 1:
                self._split_child(node, i)
                # After split, decide which of the two children to descend into
                if key >= node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BPlusTreeNode, index: int):
        """
        Split parent.children[index] into two nodes.

        Leaf split:
            - Right half stays in original node.
            - Left half goes into a new node.
            - Middle key is COPIED up to the parent (stays in leaves too).
            - Linked list (next pointer) is updated.

        Internal split:
            - Middle key is PROMOTED up (removed from child).
            - Left child keeps keys[:mid], right child gets keys[mid+1:].
        """
        order    = self.order
        child    = parent.children[index]
        mid      = len(child.keys) // 2

        new_node = BPlusTreeNode(order=order, is_leaf=child.is_leaf)
        new_node.parent = parent

        if child.is_leaf:
            # --- Leaf split ---
            # New node gets the right half (including mid key — copy-up)
            new_node.keys   = child.keys[mid:]
            new_node.values = child.values[mid:]
            child.keys      = child.keys[:mid]
            child.values    = child.values[:mid]

            # Maintain linked list
            new_node.next = child.next
            child.next    = new_node

            # Copy the first key of new_node up to the parent
            promote_key = new_node.keys[0]
        else:
            # --- Internal split ---
            # Middle key is promoted (removed from child)
            promote_key      = child.keys[mid]
            new_node.keys    = child.keys[mid + 1:]
            new_node.children = child.children[mid + 1:]
            child.keys       = child.keys[:mid]
            child.children   = child.children[:mid + 1]

            # Re-parent the moved children
            for c in new_node.children:
                c.parent = new_node

        # Insert the promoted key and new child into parent
        parent.keys.insert(index, promote_key)
        parent.children.insert(index + 1, new_node)

    # ================================================================== #
    #  DELETE                                                              #
    # ================================================================== #

    def delete(self, key) -> bool:
        """
        Delete a key from the B+ Tree.
        - Handles underflow by borrowing from siblings or merging nodes.
        - Shrinks the root if it becomes empty.
        Returns True if deletion succeeded, False if key not found.
        Time complexity: O(log n)
        """
        if self.search(key) is None:
            return False
        self._delete(self.root, key)

        # If root has no keys but has a child, shrink the tree
        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
            self.root.parent = None

        return True

    def _delete(self, node: BPlusTreeNode, key):
        """Recursive deletion handler for both leaf and internal nodes."""
        if node.is_leaf:
            if key in node.keys:
                i = node.keys.index(key)
                node.keys.pop(i)
                node.values.pop(i)
        else:
            i = node.find_child_index(key)
            child = node.children[i]

            # Ensure child won't underflow after deletion
            if len(child.keys) <= self._min_keys:
                self._fill_child(node, i)
                # After fill, the tree may have restructured — re-find position
                i = node.find_child_index(key)
                if i >= len(node.children):
                    i = len(node.children) - 1

            self._delete(node.children[i], key)

            # Fix parent key if deleted key was a separator
            if key in node.keys:
                idx = node.keys.index(key)
                # Replace separator with the new smallest key of right subtree
                node.keys[idx] = self._get_min_leaf_key(node.children[idx + 1])

    def _fill_child(self, node: BPlusTreeNode, index: int):
        """
        Ensure node.children[index] has enough keys to allow deletion.
        Strategy:
          1. Borrow from left sibling if it has excess.
          2. Borrow from right sibling if it has excess.
          3. Otherwise merge with a sibling.
        """
        if index > 0 and len(node.children[index - 1].keys) > self._min_keys:
            self._borrow_from_prev(node, index)
        elif index < len(node.children) - 1 and len(node.children[index + 1].keys) > self._min_keys:
            self._borrow_from_next(node, index)
        else:
            # Merge: prefer merging with left sibling
            if index > 0:
                self._merge(node, index - 1)
            else:
                self._merge(node, index)

    def _borrow_from_prev(self, node: BPlusTreeNode, index: int):
        """
        Borrow the rightmost key from the left sibling.
        - Leaf: move key+value directly; update parent separator.
        - Internal: rotate key through parent.
        """
        child  = node.children[index]
        sibling = node.children[index - 1]

        if child.is_leaf:
            # Move sibling's last key/value to front of child
            child.keys.insert(0, sibling.keys.pop())
            child.values.insert(0, sibling.values.pop())
            # Update the parent separator to new first key of child
            node.keys[index - 1] = child.keys[0]
        else:
            # Rotate: parent key comes down, sibling's last key goes up
            child.keys.insert(0, node.keys[index - 1])
            node.keys[index - 1] = sibling.keys.pop()
            # Move sibling's last child pointer to child
            moved_child = sibling.children.pop()
            moved_child.parent = child
            child.children.insert(0, moved_child)

    def _borrow_from_next(self, node: BPlusTreeNode, index: int):
        """
        Borrow the leftmost key from the right sibling.
        - Leaf: move key+value directly; update parent separator.
        - Internal: rotate key through parent.
        """
        child   = node.children[index]
        sibling = node.children[index + 1]

        if child.is_leaf:
            # Move sibling's first key/value to end of child
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))
            # Update parent separator to sibling's new first key
            node.keys[index] = sibling.keys[0]
        else:
            # Rotate: parent key comes down, sibling's first key goes up
            child.keys.append(node.keys[index])
            node.keys[index] = sibling.keys.pop(0)
            # Move sibling's first child pointer to child
            moved_child = sibling.children.pop(0)
            moved_child.parent = child
            child.children.append(moved_child)

    def _merge(self, node: BPlusTreeNode, index: int):
        """
        Merge node.children[index] with node.children[index + 1].
        The right child is absorbed into the left, then removed from parent.

        - Leaf merge: simply concatenate keys/values + fix next pointer.
        - Internal merge: pull down the parent separator key, then concatenate.
        """
        left  = node.children[index]
        right = node.children[index + 1]

        if left.is_leaf:
            # Concatenate leaf data and fix linked list
            left.keys   += right.keys
            left.values += right.values
            left.next    = right.next
        else:
            # Pull the parent separator down into left
            left.keys.append(node.keys[index])
            left.keys      += right.keys
            left.children  += right.children
            for c in right.children:
                c.parent = left

        # Remove the separator key and right child from parent
        node.keys.pop(index)
        node.children.pop(index + 1)

    def _get_min_leaf_key(self, node: BPlusTreeNode):
        """Descend to the leftmost leaf and return its smallest key."""
        while not node.is_leaf:
            node = node.children[0]
        return node.keys[0]

    # ================================================================== #
    #  UPDATE                                                              #
    # ================================================================== #

    def update(self, key, new_value) -> bool:
        """
        Update the value associated with an existing key.
        Returns True if key was found and updated, False otherwise.
        Time complexity: O(log n)
        """
        leaf = self._find_leaf(key)
        if key in leaf.keys:
            leaf.values[leaf.keys.index(key)] = new_value
            return True
        return False

    # ================================================================== #
    #  RANGE QUERY                                                         #
    # ================================================================== #

    def range_query(self, start_key, end_key) -> list:
        """
        Return all (key, value) pairs where start_key <= key <= end_key.
        Uses the leaf linked list for O(log n + k) performance,
        where k is the number of results returned.
        """
        results = []
        leaf    = self._find_leaf(start_key)

        while leaf is not None:
            for i, k in enumerate(leaf.keys):
                if k > end_key:
                    return results
                if k >= start_key:
                    results.append((k, leaf.values[i]))
            leaf = leaf.next

        return results

    # ================================================================== #
    #  GET ALL                                                             #
    # ================================================================== #

    def get_all(self) -> list:
        """
        Return all (key, value) pairs in sorted order.
        Traverses the leaf linked list from the leftmost leaf.
        Time complexity: O(n)
        """
        results = []
        node    = self.root
        # Walk to leftmost leaf
        while not node.is_leaf:
            node = node.children[0]
        # Follow next pointers
        while node is not None:
            for k, v in zip(node.keys, node.values):
                results.append((k, v))
            node = node.next
        return results

    # ================================================================== #
    #  VISUALISATION (Graphviz)                                            #
    # ================================================================== #

    def visualize_tree(self):
        """
        Generate and return a Graphviz Digraph of the B+ Tree.
        - Internal nodes: rectangular, purple-filled.
        - Leaf nodes: rounded, teal-filled.
        - Leaf next-pointers: dashed blue edges.
        
        Usage:
            dot = tree.visualize_tree()
            dot.render("bplustree", format="png", view=True)
        """
        from graphviz import Digraph
        dot = Digraph("BPlusTree")
        dot.attr(rankdir="TB", splines="polyline")
        dot.attr("node", fontname="Helvetica", fontsize="11")

        self._add_nodes(dot, self.root)
        self._add_edges(dot, self.root)
        return dot

    def _add_nodes(self, dot, node: BPlusTreeNode):
        """Recursively add all nodes to the Graphviz object."""
        node_id = str(id(node))
        label   = " | ".join(str(k) for k in node.keys)

        if node.is_leaf:
            dot.node(node_id, label=label,
                     shape="record", style="filled,rounded",
                     fillcolor="#5DCAA5", fontcolor="white")
        else:
            dot.node(node_id, label=label,
                     shape="record", style="filled",
                     fillcolor="#7F77DD", fontcolor="white")

        for child in node.children:
            self._add_nodes(dot, child)

    def _add_edges(self, dot, node: BPlusTreeNode):
        """Add parent→child edges and dashed leaf→leaf next-pointer edges."""
        node_id = str(id(node))

        for child in node.children:
            dot.edge(node_id, str(id(child)), color="#444444")
            self._add_edges(dot, child)

        # Dashed next-pointer between leaf nodes
        if node.is_leaf and node.next is not None:
            dot.edge(node_id, str(id(node.next)),
                     style="dashed", color="#185FA5",
                     constraint="false", label="next")

    # ================================================================== #
    #  DUNDER                                                              #
    # ================================================================== #

    def __repr__(self) -> str:
        return f"BPlusTree(order={self.order}, size={len(self.get_all())})"

    def __len__(self) -> int:
        return len(self.get_all())

    def __contains__(self, key) -> bool:
        return self.search(key) is not None