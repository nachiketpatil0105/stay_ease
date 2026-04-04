import math


class BPlusTreeNode:
    def __init__(self, order, is_leaf=False):
        # 'order' dictates our maximum capacity (maximum number of children)
        self.order = order
        self.is_leaf = is_leaf
        
        # Every node, regardless of type, needs keys to maintain sorted order
        self.keys = []
        
        # Leaves store the actual database records/values [cite: 45]
        self.values = []
        # Leaves link to their right neighbor for fast range queries [cite: 44, 58, 278]
        self.next_leaf = None 
        
        # Internal nodes don't store data; they store pointers to other nodes
        self.children = []

    def is_full(self):
        """Check if this node has hit its key limit."""
        # By definition, a B+ tree node of a given order 'm' can hold at most 'm - 1' keys
        return len(self.keys) >= self.order - 1

    def insert_at_leaf(self, key, value):
        """
        Inserts a key and its corresponding value into a leaf node.
        We must ensure the keys stay in strictly increasing order.
        """
        # Safety check: we should only be doing this in a leaf!
        if not self.is_leaf:
            raise ValueError("Cannot insert data into an internal routing node.")
            
        # Walk through the keys to find the exact right spot
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1
            
        # Handle duplicates (Updates)
        # If the key is already here, we just update the existing record
        if idx < len(self.keys) and self.keys[idx] == key:
            self.values[idx] = value
            return False # Returning False lets our main tree know it was just an update
            
        # Insert the brand new key and value at the found index
        self.keys.insert(idx, key)
        self.values.insert(idx, value)
        return True # Returning True means the node grew in size

    def find_child_index(self, key):
        """
        For internal nodes, this acts as a traffic director. 
        It looks at the keys and figures out which child pointer to follow down the tree.
        """
        # Safety check: leaves don't have children!
        if self.is_leaf:
            raise ValueError("Leaf nodes do not have children to search through.")
            
        idx = 0
        # We move right as long as the target key is greater than or equal to the current key
        while idx < len(self.keys) and key >= self.keys[idx]:
            idx += 1
            
        # This index perfectly matches the position in the self.children list
        return idx

    def split_node(self):
        """
        Splits a full node into two, returning the key to be promoted 
        and the newly created right-sibling node.
        """
        mid_index = len(self.keys) // 2
        
        # Create the new right-hand buddy node. It shares the same leaf status.
        right_node = BPlusTreeNode(self.order, is_leaf=self.is_leaf)
        
        if self.is_leaf:
            # LEAF NODE SPLIT
            # Give the right node the second half of the keys and values
            right_node.keys = self.keys[mid_index:]
            right_node.values = self.values[mid_index:]
            
            # Keep the first half for the current node
            self.keys = self.keys[:mid_index]
            self.values = self.values[:mid_index]
            
            # Re-wire the linked list so range queries still work seamlessly
            right_node.next_leaf = self.next_leaf
            self.next_leaf = right_node
            
            # For leaves, we COPY the first key of the right node to push up
            promoted_key = right_node.keys[0]
            
        else:
            # INTERNAL NODE SPLIT
            # The middle key is removed entirely from this level to be pushed up
            promoted_key = self.keys[mid_index]
            
            # Give the right node the keys and children AFTER the middle key
            right_node.keys = self.keys[mid_index + 1:]
            right_node.children = self.children[mid_index + 1:]
            
            # Keep the keys and children BEFORE the middle key for the current node
            self.keys = self.keys[:mid_index]
            self.children = self.children[:mid_index + 1]
            
        return promoted_key, right_node

    def get_value(self, key):
        """
        Searches this leaf node for a specific key and returns its value.
        """
        # Safety check: internal nodes don't hold actual data values
        if not self.is_leaf:
            return None
            
        # Scan through the keys. If we find a match, return the value at the exact same index.
        for idx, k in enumerate(self.keys):
            if k == key:
                return self.values[idx]
                
        # If we check all keys and don't find it, it doesn't exist here
        return None

    def remove_from_leaf(self, key):
        """
        Finds a key in this leaf node and removes both it and its corresponding value.
        """
        # Safety check: we only delete raw data from leaves
        if not self.is_leaf:
            return False
            
        for idx, k in enumerate(self.keys):
            if k == key:
                # Pop removes the item at the specific index from the list
                self.keys.pop(idx)
                self.values.pop(idx)
                return True # Deletion successful
                
        return False # Key wasn't found
    
class BPlusTree:
    def __init__(self, order=4):
        self.order = order
        # The tree always starts with a single, empty leaf node acting as the root
        self.root = BPlusTreeNode(order=self.order, is_leaf=True)

    def search(self, key):
        """
        Exact Search: Returns the value for a given key, or None if not found.
        """
        current_node = self.root
        
        # Drill down through internal nodes until we hit a leaf
        while not current_node.is_leaf:
            # Our smart node tells us exactly which child pointer to follow
            idx = current_node.find_child_index(key)
            current_node = current_node.children[idx]
            
        # Now we are at the correct leaf, just ask the leaf for the value
        return current_node.get_value(key)

    def range_query(self, start_key, end_key):
        """
        Range Query: Returns a list of (key, value) tuples within the range.
        This takes advantage of the linked list connecting our leaf nodes!
        """
        results = []
        current_node = self.root
        
        # Drill down to find the leaf where the `start_key` belongs
        while not current_node.is_leaf:
            idx = current_node.find_child_index(start_key)
            current_node = current_node.children[idx]
            
        # Surf the linked list of leaves!
        while current_node is not None:
            # Check every key in the current leaf
            for i, k in enumerate(current_node.keys):
                if start_key <= k <= end_key:
                    results.append((k, current_node.values[i]))
                elif k > end_key:
                    # Since keys are sorted, once we pass end_key, we are completely done!
                    # We don't even need to look at the rest of the tree.
                    return results
            
            # Jump to the right neighbor using the pointer we set up during splits
            current_node = current_node.next_leaf
            
        return results

    def insert(self, key, value):
        """
        The main entry point for adding new data.
        It handles the special case where the very top of the tree (the root) is full.
        """
        # If the root has hit its capacity, the entire tree must grow one level taller
        if self.root.is_full():
            # Create a new, empty internal node to become the new root
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            
            # The old root becomes the first child of this new root
            new_root.children.append(self.root)
            
            # Force the old root to split. It gives us a key to pull up and a new right child.
            promoted_key, right_child = self.root.split_node()
            
            # Slot the promoted key and the new right child into our new root
            new_root.keys.append(promoted_key)
            new_root.children.append(right_child)
            
            # Officially update the tree's root pointer
            self.root = new_root
            
        # Now that we are sure the root has breathing room, we start the descent
        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, current_node, key, value):
        """
        A recursive helper that navigates down the tree.
        It splits any full child nodes it encounters ON THE WAY DOWN to prevent bottlenecks.
        """
        if current_node.is_leaf:
            # Base Case: We hit the bottom! Drop the data in.
            current_node.insert_at_leaf(key, value)
        else:
            # Recursive Case: We are in an internal node. Find which path to take.
            idx = current_node.find_child_index(key)
            child_node = current_node.children[idx]
            
            # Pre-emptive split: If the child we are about to visit is full, split it FIRST.
            if child_node.is_full():
                promoted_key, right_child = child_node.split_node()
                
                # Insert the promoted key and new child pointer into the current internal node
                current_node.keys.insert(idx, promoted_key)
                current_node.children.insert(idx + 1, right_child)
                
                # Because we just split the child, the key we are trying to insert might 
                # actually belong in the newly created right child. We need to check!
                if key >= current_node.keys[idx]:
                    idx += 1
                    child_node = current_node.children[idx]
                    
            # Now safely move down to the (guaranteed not-full) child
            self._insert_non_full(child_node, key, value)

    def get_all(self):
        """
        Returns every single (key, value) pair in the database index.
        This uses an in-order traversal by riding the leaf linked-list.
        """
        results = []
        current_node = self.root
        
        # Step 1: Drop straight down the far-left edge of the tree
        while not current_node.is_leaf:
            current_node = current_node.children[0]
            
        # Step 2: Surf the linked list from left to right!
        while current_node is not None:
            for i in range(len(current_node.keys)):
                results.append((current_node.keys[i], current_node.values[i]))
            current_node = current_node.next_leaf
            
        return results

    def visualize_tree(self, title="Binary Tree"):
        """
        Generates a Graphviz Digraph to visually map out our nodes and pointers.
        This is explicitly required for the assignment report and video.
        """
        try:
            from graphviz import Digraph
        except ImportError:
            print("Run: pip install graphviz")
            return None

        dot = Digraph()
        dot.attr(rankdir='TB')
        # FIX 1: Changed 'ortho' to 'polyline' to respect HTML ports
        dot.attr('graph', splines='polyline', nodesep='0.8', ranksep='1.2',
                label=title, labelloc='t', labeljust='c', fontsize='16', fontname='Helvetica-Bold')
        dot.attr('node', fontname='Helvetica', fontsize='12')

        if self.root:
            self._add_nodes(dot, self.root)
            self._add_edges(dot, self.root)

        return dot

    def _add_nodes(self, dot, node):
        # FIX 2: Prefixing with "node_" so Graphviz properly parses the ports
        node_id = f"node_{id(node)}"

        if node.is_leaf:
            if node.keys:
                cells = "".join(
                    f'<TD BORDER="1" PORT="k{i}" CELLPADDING="6" STYLE="ROUNDED">'
                    f'<FONT COLOR="#1A5276"><B>{k}</B></FONT></TD>'
                    for i, k in enumerate(node.keys)
                )
            else:
                cells = '<TD BORDER="1" CELLPADDING="6"><I>empty</I></TD>'

            table = (
                '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3" CELLPADDING="0">'
                f'<TR>{cells}</TR>'
                '</TABLE>>'
            )
            dot.node(node_id, label=table, shape='none', margin='0')

        else:
            num_keys = len(node.keys)
            cells = ""

            for i in range(num_keys):
                cells += (
                    f'<TD BORDER="1" PORT="p{i}" CELLPADDING="6" WIDTH="18" '
                    f'BGCOLOR="#F0E6D3"> </TD>'
                )
                cells += (
                    f'<TD BORDER="1" CELLPADDING="6" BGCOLOR="#FAD7A0">'
                    f'<FONT COLOR="#784212"><B>{node.keys[i]}</B></FONT></TD>'
                )

            cells += (
                f'<TD BORDER="1" PORT="p{num_keys}" CELLPADDING="6" WIDTH="18" '
                f'BGCOLOR="#F0E6D3"> </TD>'
            )

            table = (
                '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
                f'<TR>{cells}</TR>'
                '</TABLE>>'
            )
            dot.node(node_id, label=table, shape='none', margin='0')

        if not node.is_leaf:
            for child in node.children:
                self._add_nodes(dot, child)


    def _add_edges(self, dot, node):
        # FIX 2: Apply the exact same prefix here
        node_id = f"node_{id(node)}"

        if not node.is_leaf:
            for i, child in enumerate(node.children):
                child_id = f"node_{id(child)}"
                dot.edge(
                    f'{node_id}:p{i}:s',
                    f'{child_id}:n',
                    color="#2C3E50",
                    penwidth="1.5",
                    arrowsize="0.7"
                )
                self._add_edges(dot, child)

        elif node.next_leaf:
            last_port = f'k{len(node.keys) - 1}'
            next_leaf_id = f"node_{id(node.next_leaf)}"
            dot.edge(
                f'{node_id}:{last_port}:e',
                f'{next_leaf_id}:k0:w',
                style="dashed",
                color="#1D8348",
                constraint="false",
                arrowsize="0.7"
            )

    def delete(self, key):
        """
        Deletes a key from the B+ tree[cite: 232].
        Updates the root if it becomes empty[cite: 234].
        Returns True if deletion succeeded, False otherwise[cite: 235].
        """
        if len(self.root.keys) == 0:
            return False

        # Start the recursive deletion process
        success = self._delete(self.root, key)

        # If the root is completely empty but still has a child, 
        # the tree shrinks in height! We just make the child the new root.
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]

        return success

    def _delete(self, current_node, key):
        """
        Recursive helper for deletion[cite: 240].
        Ensures all nodes maintain minimum keys after deletion[cite: 241].
        """
        if current_node.is_leaf:
            # Base Case: Try to remove the key directly from the leaf
            return current_node.remove_from_leaf(key)
        else:
            # Recursive Case: Find which child should contain the key and go down
            idx = current_node.find_child_index(key)
            child_node = current_node.children[idx]

            # Recursively delete from that child
            success = self._delete(child_node, key)

            # UNDERFLOW CHECK: A node must be at least half full.
            # If our child lost too many keys, we must step in and fix it.
            min_keys = self.order // 2
            if len(child_node.keys) < min_keys:
                self._fill_child(current_node, idx)

            return success

    def _fill_child(self, parent_node, idx):
        """
        Ensures child at given index has enough keys by borrowing from siblings or merging[cite: 246, 247].
        """
        min_keys = self.order // 2

        # Strategy 1: Try borrowing from the LEFT sibling [cite: 253]
        if idx > 0 and len(parent_node.children[idx - 1].keys) > min_keys:
            self._borrow_from_prev(parent_node, idx)

        # Strategy 2: Try borrowing from the RIGHT sibling [cite: 258]
        elif idx < len(parent_node.children) - 1 and len(parent_node.children[idx + 1].keys) > min_keys:
            self._borrow_from_next(parent_node, idx)

        # Strategy 3: If siblings are also poor, we must MERGE them together [cite: 263]
        else:
            if idx < len(parent_node.children) - 1:
                # Merge the child with its right sibling
                self._merge(parent_node, idx)
            else:
                # If it's the very last child, merge it with its left sibling
                self._merge(parent_node, idx - 1)

    def _borrow_from_prev(self, parent_node, idx):
        """Borrow a key from the left sibling to prevent underflow[cite: 252, 253]."""
        child = parent_node.children[idx]
        left_sibling = parent_node.children[idx - 1]

        if child.is_leaf:
            # Slide the sibling's last piece of data into the front of our child
            child.keys.insert(0, left_sibling.keys.pop())
            child.values.insert(0, left_sibling.values.pop())
            # Update the parent's routing key
            parent_node.keys[idx - 1] = child.keys[0]
        else:
            # For internal nodes, we pull a key DOWN from the parent, 
            # and push the sibling's last key UP to the parent.
            child.keys.insert(0, parent_node.keys[idx - 1])
            parent_node.keys[idx - 1] = left_sibling.keys.pop()
            child.children.insert(0, left_sibling.children.pop())

    def _borrow_from_next(self, parent_node, idx):
        """Borrow a key from the right sibling to prevent underflow[cite: 257, 258]."""
        child = parent_node.children[idx]
        right_sibling = parent_node.children[idx + 1]

        if child.is_leaf:
            # Pull the sibling's first piece of data into the end of our child
            child.keys.append(right_sibling.keys.pop(0))
            child.values.append(right_sibling.values.pop(0))
            # Update the parent's routing key
            parent_node.keys[idx] = right_sibling.keys[0]
        else:
            # Pull parent key DOWN, push sibling's first key UP
            child.keys.append(parent_node.keys[idx])
            parent_node.keys[idx] = right_sibling.keys.pop(0)
            child.children.append(right_sibling.children.pop(0))

    def _merge(self, parent_node, idx):
        """Merge child at index with its right sibling. Update parent keys[cite: 262, 263]."""
        left_child = parent_node.children[idx]
        right_child = parent_node.children[idx + 1]

        if left_child.is_leaf:
            # Combine all keys and values
            left_child.keys.extend(right_child.keys)
            left_child.values.extend(right_child.values)
            # Crucial step: Re-wire the linked list past the deleted node!
            left_child.next_leaf = right_child.next_leaf 
        else:
            # Internal merge requires pulling the routing key DOWN from the parent
            left_child.keys.append(parent_node.keys[idx])
            left_child.keys.extend(right_child.keys)
            left_child.children.extend(right_child.children)

        # Finally, remove the stale routing key and the defunct right child from the parent
        parent_node.keys.pop(idx)
        parent_node.children.pop(idx + 1)

    def update(self, key, new_value):
        """
        Updates the value associated with an existing key.
        Returns True if successful, False if the key doesn't exist.
        """
        current_node = self.root
        
        # Step 1: Drill down through internal nodes until we hit the correct leaf
        while not current_node.is_leaf:
            idx = current_node.find_child_index(key)
            current_node = current_node.children[idx]
            
        # Step 2: Scan the leaf for the exact key
        for i, k in enumerate(current_node.keys):
            if k == key:
                # Key found! Overwrite the old value with the new one.
                current_node.values[i] = new_value
                return True
                
        # If we loop through the whole leaf and don't find it, the key isn't in our database
        return False