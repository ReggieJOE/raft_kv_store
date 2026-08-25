from raft_node import RaftNode, State

class RaftKVStore:
    def __init__(self, node_id, peers):
        self.node = RaftNode(node_id, peers)

    def set(self, key, value):
        if self.node.state != State.LEADER:
            print(f"Node {self.node.node_id} is not leader — "
                  f"redirecting to Node {self.node.leader_id}")
            return False
        entry = {
            'term': self.node.current_term,
            'key': key,
            'value': value
        }
        self.node.log.append(entry)
        self.node.kv_store[key] = value
        print(f"Node {self.node.node_id} SET {key}={value} | "
              f"log length: {len(self.node.log)}")
        return True

    def get(self, key):
        value = self.node.kv_store.get(key, None)
        print(f"Node {self.node.node_id} GET {key}={value}")
        return value

    def show_log(self):
        print(f"\nNode {self.node.node_id} log:")
        for i, entry in enumerate(self.node.log):
            print(f"  [{i}] term={entry['term']} | "
                  f"SET {entry['key']}={entry['value']}")

if __name__ == "__main__":
    # Create 5 KV store nodes
    stores = [
        RaftKVStore(node_id=i, peers=[j for j in range(1,6) if j != i])
        for i in range(1, 6)
    ]

    # Node 1 becomes leader
    stores[0].node.start_election()
    for store in stores[1:]:
        stores[0].node.receive_vote(
            from_node=store.node.node_id,
            term=stores[0].node.current_term,
            granted=True
        )

    # Heartbeats so followers know leader
    for store in stores[1:]:
        store.node.receive_heartbeat(
            from_leader=1,
            term=stores[0].node.current_term
        )

    print("\n--- Testing KV Store ---")
    stores[0].set("name", "Reggie")
    stores[0].set("university", "KNUST")
    stores[0].set("country", "Ghana")

    stores[0].get("name")
    stores[0].get("university")

    print("\n--- Attempting write via follower ---")
    stores[1].set("name", "John")

    stores[0].show_log()