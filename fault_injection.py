from kv_store import RaftKVStore
from raft_node import State

def setup_cluster():
    """Create and elect a leader"""
    stores = [
        RaftKVStore(node_id=i, peers=[j for j in range(1,6) if j != i])
        for i in range(1, 6)
    ]
    stores[0].node.start_election()
    for store in stores[1:]:
        stores[0].node.receive_vote(
            from_node=store.node.node_id,
            term=stores[0].node.current_term,
            granted=True
        )
    for store in stores[1:]:
        store.node.receive_heartbeat(
            from_leader=1,
            term=stores[0].node.current_term
        )
    return stores

if __name__ == "__main__":
    stores = setup_cluster()

    print("\n--- Phase 1: Normal writes ---")
    stores[0].set("name", "Reggie")
    stores[0].set("university", "KNUST")

    print("\n--- Phase 2: Kill the leader (Node 1) ---")
    stores[0].node.state = State.FOLLOWER  # simulate crash
    print(f"Node 1 crashed — state forced to FOLLOWER")

    print("\n--- Phase 3: New election ---")
    # Node 2 times out and starts election
    stores[1].node.start_election()
    for store in stores[2:]:
        stores[1].node.receive_vote(
            from_node=store.node.node_id,
            term=stores[1].node.current_term,
            granted=True
        )

    # Update all nodes about new leader
    for store in [stores[0]] + stores[2:]:
        store.node.receive_heartbeat(
            from_leader=2,
            term=stores[1].node.current_term
        )

    print(f"\nCluster state after leader failure:")
    for store in stores:
        print(f"  {store.node}")

    print("\n--- Phase 4: Write to new leader ---")
    stores[1].set("country", "Ghana")
    stores[1].set("goal", "PhD 2027")

    print("\n--- Phase 5: Old leader tries to write (should fail) ---")
    stores[0].set("name", "impostor")

    print("\n--- New leader log ---")
    stores[1].show_log()