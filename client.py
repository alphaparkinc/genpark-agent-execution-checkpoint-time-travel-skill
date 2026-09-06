"""
Agent Execution Checkpointing and Time-Travel Rollback Engine.
Zero external dependencies, standard library only.
"""

import time
import copy
import hashlib
from typing import Dict, List, Any, Optional

class AgentCheckpointTimeTravelClient:
    """
    Manages deterministic snapshots of agent execution states:
    - Save point registration with SHA-256 state hashing
    - Time-travel rollback to past checkpoints
    - Thread branching from historical state snapshots
    """

    def __init__(self):
        # thread_id -> list of checkpoint dicts
        self.threads: Dict[str, List[Dict[str, Any]]] = {}

    def _hash_state(self, state: Dict[str, Any]) -> str:
        s_str = str(sorted(state.items()))
        return hashlib.sha256(s_str.encode("utf-8")).hexdigest()[:12]

    def save_checkpoint(self, thread_id: str, step_index: int, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Saves deep copy snapshot of agent state for a given execution thread."""
        if thread_id not in self.threads:
            self.threads[thread_id] = []

        checkpoint_id = f"chk_{step_index}_{self._hash_state(state)}"
        entry = {
            "checkpoint_id": checkpoint_id,
            "step_index": step_index,
            "timestamp": round(time.time(), 3),
            "state": copy.deepcopy(state),
            "metadata": metadata or {}
        }
        self.threads[thread_id].append(entry)
        return checkpoint_id

    def get_checkpoint(self, thread_id: str, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves exact state snapshot for a given checkpoint ID."""
        for c in self.threads.get(thread_id, []):
            if c["checkpoint_id"] == checkpoint_id:
                return copy.deepcopy(c)
        return None

    def rollback(self, thread_id: str, target_checkpoint_id: str) -> Dict[str, Any]:
        """Rolls back thread execution to target checkpoint, discarding subsequent states."""
        history = self.threads.get(thread_id, [])
        idx = -1
        for i, c in enumerate(history):
            if c["checkpoint_id"] == target_checkpoint_id:
                idx = i
                break

        if idx == -1:
            raise KeyError(f"Checkpoint '{target_checkpoint_id}' not found in thread '{thread_id}'")

        discarded_count = len(history) - (idx + 1)
        self.threads[thread_id] = history[:idx + 1]
        return {
            "status": "ROLLED_BACK",
            "current_checkpoint": self.threads[thread_id][-1]["checkpoint_id"],
            "restored_state": copy.deepcopy(self.threads[thread_id][-1]["state"]),
            "discarded_checkpoints": discarded_count
        }

    def fork_branch(self, source_thread_id: str, checkpoint_id: str, new_thread_id: str) -> Dict[str, Any]:
        """Forks a new thread history starting from a historical checkpoint."""
        source_chk = self.get_checkpoint(source_thread_id, checkpoint_id)
        if not source_chk:
            raise KeyError(f"Checkpoint '{checkpoint_id}' not found in source thread '{source_thread_id}'")

        self.threads[new_thread_id] = [source_chk]
        return {
            "status": "BRANCHED",
            "new_thread_id": new_thread_id,
            "origin_checkpoint": checkpoint_id,
            "initial_state": source_chk["state"]
        }
