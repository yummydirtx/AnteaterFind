from collections import OrderedDict

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation for storing index terms.
    """

    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        """Get a value from the cache, returning None if not present"""
        if key in self.cache:
            # Move to end to show this was recently used
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        """Add a value to the cache, possibly evicting older entries"""
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            # Evict least recently used item
            self.cache.popitem(last = False)
