class BruteForceDB:
    def __init__(self):
        # We use a simple list to store our data as (key, value) tuples
        self.data = []

    def insert(self, key, value=None):
        """
        Inserts a key-value pair. 
        In a brute force approach, we just append it to the end of the list (O(1)).
        """
        # Note: A true brute force DB might check for duplicates first, 
        # but appending directly matches the spirit of the assignment's baseline.
        self.data.append((key, value))

    def search(self, key):
        """
        Searches for a key using linear iteration (O(n)).
        """
        for k, v in self.data:
            if k == key:
                return v
        return None

    def delete(self, key):
        """
        Deletes a record by iterating through the list to find it (O(n)).
        """
        for i, (k, v) in enumerate(self.data):
            if k == key:
                self.data.pop(i)
                return True
        return False

    def range_query(self, start, end):
        """
        Retrieves all keys in a range by checking every single record (O(n)).
        """
        return [(k, v) for k, v in self.data if start <= k <= end]

    def get_all(self):
        """
        Returns all data.
        """
        return self.data