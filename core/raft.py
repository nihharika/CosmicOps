import time
import random
import threading
from core.network import send_request
from core.raft_storage import RaftStorage


class RaftNode:

    def __init__(self, node_id, peers, port):
        self.node_id = node_id
        self.peers = peers
        self.port = port

        self.storage = RaftStorage(node_id)

        state = self.storage.load_state()
        self.current_term = state["term"]
        self.voted_for = state["voted_for"]

        self.role = "follower"
        self.commit_index = 0
        self.log = self.storage.load_log()

        self.election_timeout = random.uniform(3, 5)
        self.last_heartbeat = time.time()

        self.lock = threading.Lock()

        threading.Thread(target=self.election_loop, daemon=True).start()

    # Election Logic

    def election_loop(self):
        while True:
            time.sleep(0.5)

            if self.role == "leader":
                continue

            if time.time() - self.last_heartbeat > self.election_timeout:
                self.start_election()

    def start_election(self):
        with self.lock:
            self.role = "candidate"
            self.current_term += 1
            self.voted_for = self.node_id
            self.storage.save_state(self.current_term, self.voted_for)

        votes = 1

        for peer in self.peers:
            try:
                response = send_request("127.0.0.1", peer, {
                    "type": "vote_request",
                    "term": self.current_term,
                    "candidate_id": self.node_id
                })
                if response.get("vote_granted"):
                    votes += 1
            except:
                pass

        if votes > (len(self.peers) + 1) // 2:
            self.become_leader()

    def become_leader(self):
        with self.lock:
            self.role = "leader"
        print(f"[{self.node_id}] LEADER term={self.current_term}")
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    # Heartbeat

    def heartbeat_loop(self):
        while self.role == "leader":
            for peer in self.peers:
                try:
                    send_request("127.0.0.1", peer, {
                        "type": "heartbeat",
                        "term": self.current_term
                    })
                except:
                    pass
            time.sleep(1)

    # Replication

    def replicate_log(self, value):
        if self.role != "leader":
            return {"error": "not leader"}

        entry = {
            "term": self.current_term,
            "value": value
        }

        self.storage.append_log(entry)
        self.log.append(entry)

        acks = 1

        for peer in self.peers:
            try:
                response = send_request("127.0.0.1", peer, {
                    "type": "append_entries",
                    "term": self.current_term,
                    "entry": entry
                })
                if response.get("success"):
                    acks += 1
            except:
                pass

        if acks > (len(self.peers) + 1) // 2:
            self.commit_index += 1
            return {"status": "committed"}

        return {"status": "failed"}

    # RPC Handlers

    def handle_vote_request(self, term, candidate_id):
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.role = "follower"
            self.storage.save_state(self.current_term, self.voted_for)

        if self.voted_for is None:
            self.voted_for = candidate_id
            self.storage.save_state(self.current_term, self.voted_for)
            return {"vote_granted": True}

        return {"vote_granted": False}

    def handle_heartbeat(self, term):
        if term >= self.current_term:
            self.current_term = term
            self.role = "follower"
            self.last_heartbeat = time.time()
            self.storage.save_state(self.current_term, self.voted_for)
        return {"status": "ok"}

    def handle_append_entries(self, term, entry):
        if term >= self.current_term:
            self.current_term = term
            self.role = "follower"
            self.storage.append_log(entry)
            self.log.append(entry)
            return {"success": True}
        return {"success": False}