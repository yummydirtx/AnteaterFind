from collections import OrderedDict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation for storing index terms.
    """

    def __init__(self, capacity):
        """Intialize cache"""
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        """
            Retrieve the value associated with the given key from the LRU cache.
        Args:
            key: The unique identifier for the cached entry.
        Returns:
            Get a value from the cache, returning None if not present
        """
        if key in self.cache:
            # Move to end to show this was recently used
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        """Add/Update a value to the cache as key-value pair, and evicting older entries
        Args:
            key: The unique identifier for the cached entry.
            value: The value to associate with the key.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            # Evict least recently used item
            self.cache.popitem(last = False)
