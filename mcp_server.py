"""
MCP Server for genpark-agent-execution-checkpoint-time-travel-skill
Standard JSON-RPC 2.0 protocol over stdio.
"""

import sys
import json
from client import AgentCheckpointTimeTravelClient

engine = AgentCheckpointTimeTravelClient()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "save_checkpoint",
                        "description": "Persist an agent execution state snapshot.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "thread_id": {"type": "string"},
                                "step": {"type": "integer"},
                                "state": {"type": "object"}
                            },
                            "required": ["thread_id", "step", "state"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "save_checkpoint":
            chk_id = engine.save_checkpoint(args["thread_id"], args["step"], args["state"])
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"checkpoint_id": chk_id})}]
                }
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
