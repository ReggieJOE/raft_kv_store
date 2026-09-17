# Raft Consensus — Fault-Tolerant Distributed Key-Value Store

Distributed systems that store data across multiple servers face one 
fundamental problem: if any server can accept writes independently, 
the copies diverge and the system returns inconsistent data. Raft 
solves this by electing one leader that serialises all writes, 
replicating them to followers before committing. This project 
implements Raft leader election, a key-value store on top of it, 
and fault injection — simulating a leader crash mid-operation and 
verifying the cluster elects a new leader and continues serving 
writes automatically, without human intervention.

## What it implements

- **raft_node.py** — defines the RaftNode class with three states 
  (Follower, Candidate, Leader), randomised election timeouts, 
  quorum calculation (majority of 5 nodes = 3 votes), term-based 
  staleness detection, and heartbeat propagation. Simulates a full 
  5-node election where Node 1 wins with 3/5 votes in term 1.

- **kv_store.py** — builds a key-value store (SET/GET operations) 
  on top of RaftNode. Only the leader accepts writes — follower 
  write attempts are rejected and redirected to the current leader. 
  Every committed write is appended to the Raft log with its term 
  number, creating a durable ordered record of all operations.

- **fault_injection.py** — simulates a leader crash mid-operation. 
  Node 1 writes two records then crashes. Node 2 detects the 
  timeout, starts a new election for term 2, wins quorum, and 
  becomes the new leader. Node 1 receives a term 2 heartbeat, 
  updates its term, and steps down permanently — preventing 
  split-brain. Node 2 then accepts new writes successfully.

## Key results

| Event | Result |
|---|---|
| Node 1 elected leader | Term 1, 3/5 votes (quorum) |
| Writes before crash | name=Reggie, university=KNUST committed |
| Node 1 crash detected | State forced to Follower |
| New election | Node 2 elected leader, term 2 |
| Node 1 recovery | Term updated to 2, write attempts rejected |
| Writes after recovery | country=Ghana, goal=PhD 2027 committed to Node 2 |
| Split-brain prevented | Node 1 cannot start term 1 election — everyone on term 2 |

## Research connection

This project connects to Prof. Dilma Da Silva's (Texas A&M) research 
on distributed systems and cloud computing — Raft is the consensus 
foundation that makes distributed databases like CockroachDB and 
etcd reliable at scale. Prof. Ramesh Sitaraman's (UMass) CDN 
research depends on the same fault-tolerance guarantees: when 
Akamai's 240,000+ servers coordinate content placement decisions, 
the consistency properties Raft provides are what prevent stale or 
conflicting data from reaching end users. The fault injection results 
demonstrate that automated leader recovery — without human 
intervention — is achievable with a 5-node cluster tolerating up to 
2 simultaneous failures.

## How to run

```bash
pip install None  # no external dependencies — pure Python
git clone https://github.com/ReggieJOE/raft-kv-store.git
cd raft-kv-store
python raft_node.py    # single node initialisation test
python kv_store.py     # full KV store with election simulation
python fault_injection.py  # leader crash and recovery demo
```

## Author

Reginald Jojo Gwira  
Kwame Nkrumah University of Science and Technology, Ghana  
GitHub: [ReggieJOE](https://github.com/ReggieJOE)