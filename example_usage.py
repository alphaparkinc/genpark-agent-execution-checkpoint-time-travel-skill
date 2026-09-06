"""
Demonstration of genpark-agent-execution-checkpoint-time-travel-skill
"""

from client import AgentCheckpointTimeTravelClient

def main():
    engine = AgentCheckpointTimeTravelClient()
    thread_id = "session_customer_101"

    # Step 1 Checkpoint
    s1 = {"plan": ["fetch_profile", "calc_tax", "submit_order"], "status": "init"}
    c1 = engine.save_checkpoint(thread_id, 1, s1)

    # Step 2 Checkpoint
    s2 = {"plan": ["fetch_profile", "calc_tax", "submit_order"], "status": "tax_calculated", "tax_amount": 14.50}
    c2 = engine.save_checkpoint(thread_id, 2, s2)

    # Step 3 Error occurs
    s3 = {"plan": ["fetch_profile", "calc_tax", "submit_order"], "status": "payment_gateway_timeout", "error": True}
    c3 = engine.save_checkpoint(thread_id, 3, s3)

    print("=== ROLLING BACK TO PRE-PAYMENT CHECKPOINT ===")
    restored = engine.rollback(thread_id, c2)
    print(f"Restored Checkpoint: {restored['current_checkpoint']}")
    print(f"Restored Status: {restored['restored_state']['status']}")
    print(f"Discarded faulty checkpoints: {restored['discarded_checkpoints']}")

    # Fork new branch
    fork_res = engine.fork_branch(thread_id, c2, "session_customer_101_retry")
    print(f"Successfully branched into: {fork_res['new_thread_id']}")

if __name__ == "__main__":
    main()
