import time
import random
import threading
from core.network import send_request
from core.raft_storage import RaftStorage


class RaftNode:

    def __init__(self, node_id, peers, port):
        self.node_id = node_id
        self.peers = peers  # list of peer ports
        self.port = port

        self.storage = RaftStorage(node_id)

        state = self.storage.load_state()
        self.current_term = state.get("term", 0)
        self.voted_for = state.get("voted_for", None)

        self.role = "follower"
        self.commit_index = 0
        self.log = self.storage.load_log()

        self.lock = threading.Lock()

        self.reset_election_timeout()
        self.last_heartbeat = time.time()

        self.heartbeat_thread = None

        threading.Thread(target=self.election_loop, daemon=True).start()

    # Utility

    def reset_election_timeout(self):
        self.election_timeout = random.uniform(3, 5)

    def majority(self):
        # total nodes = self + peers
        total = len(self.peers) + 1
        return total // 2 + 1

    # Election Logic

    def election_loop(self):
        while True:
            time.sleep(0.5)

            with self.lock:
                if self.role == "leader":
                    continue

                if time.time() - self.last_heartbeat <= self.election_timeout:
                    continue

            self.start_election()

    def start_election(self):
        with self.lock:
            self.role = "candidate"
            self.current_term += 1
            self.voted_for = self.node_id
            self.storage.save_state(self.current_term, self.voted_for)
            self.reset_election_timeout()
            self.last_heartbeat = time.time()

            current_term = self.current_term

        votes = 1  # vote for self

        for peer in self.peers:
            try:
                response = send_request("127.0.0.1", peer, {
                    "type": "vote_request",
                    "term": current_term,
                    "candidate_id": self.node_id
                })

                if response.get("vote_granted"):
                    votes += 1

            except Exception:
                pass

        if votes >= self.majority():
            self.become_leader()

    def become_leader(self):
        with self.lock:
            self.role = "leader"

        print(f"[{self.node_id}] LEADER term={self.current_term}")

        if self.heartbeat_thread is None or not self.heartbeat_thread.is_alive():
            self.heartbeat_thread = threading.Thread(
                target=self.heartbeat_loop,
                daemon=True
            )
            self.heartbeat_thread.start()

    # Heartbeat

    def heartbeat_loop(self):
        while True:
            with self.lock:
                if self.role != "leader":
                    return
                current_term = self.current_term

            for peer in self.peers:
                try:
                    send_request("127.0.0.1", peer, {
                        "type": "heartbeat",
                        "term": current_term
                    })
                except Exception:
                    pass

            time.sleep(1)

    # Replication

    def replicate_log(self, value):
        with self.lock:
            if self.role != "leader":
                return {"error": "not leader"}

            entry = {
                "term": self.current_term,
                "value": value
            }

            self.storage.append_log(entry)
            self.log.append(entry)

            current_term = self.current_term

        acks = 1

        for peer in self.peers:
            try:
                response = send_request("127.0.0.1", peer, {
                    "type": "append_entries",
                    "term": current_term,
                    "entry": entry
                })

                if response.get("success"):
                    acks += 1

            except Exception:
                pass

        if acks >= self.majority():
            with self.lock:
                self.commit_index += 1
            return {"status": "committed"}

        return {"status": "failed"}

    # RPC Handlers

    def handle_vote_request(self, term, candidate_id):
        with self.lock:

            if term < self.current_term:
                return {"vote_granted": False}

            if term > self.current_term:
                self.current_term = term
                self.voted_for = None
                self.role = "follower"

            if self.voted_for in (None, candidate_id):
                self.voted_for = candidate_id
                self.storage.save_state(self.current_term, self.voted_for)
                self.last_heartbeat = time.time()
                self.reset_election_timeout()
                return {"vote_granted": True}

            return {"vote_granted": False}

    def handle_heartbeat(self, term):
        with self.lock:

            if term < self.current_term:
                return {"status": "stale"}

            self.current_term = term
            self.role = "follower"
            self.last_heartbeat = time.time()
            self.reset_election_timeout()
            self.storage.save_state(self.current_term, self.voted_for)

        return {"status": "ok"}

    def handle_append_entries(self, term, entry):

        with self.lock:

            if term < self.current_term:
                return {"success": False}

            self.current_term = term
            self.role = "follower"
            self.last_heartbeat = time.time()
            self.reset_election_timeout()

            self.storage.append_log(entry)
            self.log.append(entry)

        # Apply to state machine
        if entry.get("type") == "telemetry_insert":

            from telemetry.telemetry_db import TelemetryDB

            db = TelemetryDB("data/telemetry/tsdb.db")
            db.insert(entry["timestamp"], entry["value"])

        return {"success": True}