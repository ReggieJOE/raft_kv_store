import time
import random
from enum import Enum

class State(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = State.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.votes_received = 0
        self.leader_id = None
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
        self.log = []
        self.kv_store = {}
        print(f"Node {self.node_id} initialised as FOLLOWER | "
              f"timeout={self.election_timeout:.2f}s")

    def __repr__(self):
        return (f"Node({self.node_id},"
                f"state={self.state.value},"
                f"term={self.current_term})")

    def start_election(self):
        self.state = State.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        self.election_timeout = random.uniform(1.5, 3.0)
        print(f"\nNode {self.node_id} starting election for TERM {self.current_term}")
        print(f"  Voted for self — votes: {self.votes_received}/{len(self.peers)+1}")

    def receive_vote(self, from_node, term, granted):
        if term != self.current_term:
            return
        if granted:
            self.votes_received += 1
            print(f"  Node {self.node_id} received vote from Node {from_node} "
                  f"— votes: {self.votes_received}/{len(self.peers)+1}")
            quorum = (len(self.peers) + 1) // 2 + 1
            if self.votes_received >= quorum and self.state != State.LEADER:
                self.become_leader()

    def become_leader(self):
        self.state = State.LEADER
        self.leader_id = self.node_id
        print(f"\n*** Node {self.node_id} becomes LEADER for TERM "
              f"{self.current_term} ***")

    def receive_heartbeat(self, from_leader, term):
        if term >= self.current_term:
            self.current_term = term
            self.state = State.FOLLOWER
            self.leader_id = from_leader
            self.last_heartbeat = time.time()
            self.voted_for = None