import argparse
import signal
import sys

from core.network import NodeServer
from core.raft import RaftNode
from core.storage import StorageEngine


raft = None
storage = None

# Request Handler
def request_handler(request):
    global raft, storage

    req_type = request.get("type")

    # Raft internal RPCs

    if req_type == "vote_request":
        return raft.handle_vote_request(
            request["term"],
            request["candidate_id"]
        )

    if req_type == "heartbeat":
        return raft.handle_heartbeat(request["term"])

    if req_type == "append_entries":
        return raft.handle_append_entries(
            request["term"],
            request["entry"]
        )

    # Client write request

    if req_type == "write":
        # Only leader should accept writes
        if not raft.is_leader():
            return {
                "status": "error",
                "message": "Not leader"
            }

        value = request["value"]

        # Replicate via Raft
        success = raft.replicate_log(value)

        if success:
            # Apply to storage once committed
            timestamp = request.get("timestamp")
            storage.insert(timestamp, value)

            return {"status": "ok"}
        else:
            return {"status": "error", "message": "Replication failed"}

    return {"status": "unknown_request"}


# Graceful Shutdown

def shutdown_handler(signum, frame):
    global storage
    print("\nShutting down safely...")

    if storage:
        storage.flush_block()

    sys.exit(0)


# Main Entry

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", nargs="+", type=int, required=True)
    args = parser.parse_args()

    # Initialize Storage
    storage = StorageEngine()

    # Initialize Raft
    raft = RaftNode(args.id, args.peers, args.port)

    # Register shutdown hooks
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Start network server
    server = NodeServer(port=args.port)
    server.start(request_handler)