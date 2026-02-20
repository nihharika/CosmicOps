import os
import json


class RaftStorage:

    def __init__(self, node_id):
        self.dir = f"data/{node_id}"
        os.makedirs(self.dir, exist_ok=True)

        self.state_file = os.path.join(self.dir, "state.json")
        self.log_file = os.path.join(self.dir, "log.json")

        if not os.path.exists(self.state_file):
            self.save_state(0, None)

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    # Persistent State

    def save_state(self, term, voted_for):
        with open(self.state_file, "w") as f:
            json.dump({
                "term": term,
                "voted_for": voted_for
            }, f)

    def load_state(self):
        with open(self.state_file, "r") as f:
            return json.load(f)

    # Log Persistence

    def append_log(self, entry):
        logs = self.load_log()
        logs.append(entry)
        with open(self.log_file, "w") as f:
            json.dump(logs, f)

    def load_log(self):
        with open(self.log_file, "r") as f:
            return json.load(f)

    def overwrite_log(self, logs):
        with open(self.log_file, "w") as f:
            json.dump(logs, f)

    def create_snapshot(self, commit_index, log):
      snapshot_file = os.path.join(self.dir, "snapshot.json")
    with open(snapshot_file, "w") as f:
        json.dump({
            "commit_index": commit_index,
            "state": log[:commit_index]
        }, f)

    remaining = log[commit_index:]
    self.overwrite_log(remaining)
