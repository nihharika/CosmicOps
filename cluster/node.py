import argparse
from core.network import NodeServer
from core.raft import RaftNode


raft = None


def request_handler(request):

    if request["type"] == "vote_request":
        return raft.handle_vote_request(
            request["term"],
            request["candidate_id"]
        )

    if request["type"] == "heartbeat":
        return raft.handle_heartbeat(request["term"])

    if request["type"] == "append_entries":
        return raft.handle_append_entries(
            request["term"],
            request["entry"]
        )

    if request["type"] == "write":
        return raft.replicate_log(request["value"])

    return {"status": "ok"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", nargs="+", type=int, required=True)
    args = parser.parse_args()

    raft = RaftNode(args.id, args.peers, args.port)

    server = NodeServer(port=args.port)
    server.start(request_handler)