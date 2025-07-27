import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas  # Virtual nodes per physical node
        self.ring = dict()
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Returns a 32-bit hash of the key."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % (2**32)

    def add_node(self, node):
        for i in range(self.replicas):
            virtual_node_key = f"{node}#{i}"
            key_hash = self._hash(virtual_node_key)
            self.ring[key_hash] = node
            bisect.insort(self.sorted_keys, key_hash)

    def remove_node(self, node):
        for i in range(self.replicas):
            virtual_node_key = f"{node}#{i}"
            key_hash = self._hash(virtual_node_key)
            del self.ring[key_hash]
            self.sorted_keys.remove(key_hash)

    def get_node(self, key):
        """Get the node responsible for a given key."""
        if not self.ring:
            return None
        key_hash = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, key_hash) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]


# --------------------------
nodes = ['NodeA', 'NodeB', 'NodeC']
ring = ConsistentHashRing(nodes)

keys = ['user1', 'user2', 'user3', 'user4', 'user5']

print("Initial key → node mapping:")
for key in keys:
    print(f"{key} → {ring.get_node(key)}")

# Add a new node
print("\nAfter adding NodeD:")
ring.add_node('NodeD')

for key in keys:
    print(f"{key} → {ring.get_node(key)}")
