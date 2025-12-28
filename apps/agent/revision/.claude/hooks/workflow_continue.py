#!/usr/bin/env python3
"""
Stop hook: Detect incomplete workflow and prompt continuation

Prevents premature stops during multi-step workflow.
Returns continuation message based on current workflow position.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import fcntl
import time

# Paths
project_root = Path.cwd()
process_dir = project_root / "files" / "process"
workflow_state_file = process_dir / "workflow_state.json"
lock_file = process_dir / ".workflow_continue.lock"

# Cooldown to prevent rapid re-triggers
COOLDOWN_SECONDS = 3


def acquire_lock():
    """Acquire lock to prevent concurrent triggers."""
    try:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fd
    except (IOError, BlockingIOError):
        return None


def release_lock(lock_fd):
    """Release lock."""
    if lock_fd:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def check_cooldown():
    """Check if we're in cooldown period."""
    if not lock_file.exists():
        return False

    try:
        mtime = lock_file.stat().st_mtime
        elapsed = time.time() - mtime
        return elapsed < COOLDOWN_SECONDS
    except:
        return False


def get_workflow_status():
    """Get current workflow position."""
    if not workflow_state_file.exists():
        return None

    try:
        with open(workflow_state_file, 'r') as f:
            return json.load(f)
    except:
        return None


def get_continuation_message(state):
    """Generate continuation message based on workflow state."""
    status = state.get("status", "unknown")
    current_step = state.get("current_step", 0)
    steps = state.get("steps", [])
    completed_steps = state.get("completed_steps", [])

    if status == "completed":
        return (False, "Workflow already completed.")

    if status == "initialized":
        # Just started, invoke first step
        if steps:
            return (True, f"Workflow just started. Invoke 'orchestrating-workflow' skill to begin with '{steps[0]}' subagent.")
        return (False, "")

    if status == "in_progress":
        if current_step < len(steps):
            current_agent = steps[current_step]
            return (True, f"Workflow in progress. Current step: {current_agent}. Invoke 'orchestrating-workflow' skill to continue.")
        else:
            return (False, "All steps completed.")

    return (False, "")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Check cooldown
if check_cooldown():
    sys.exit(0)

# Try to acquire lock
lock_fd = acquire_lock()
if not lock_fd:
    sys.exit(0)

try:
    # Get workflow status
    state = get_workflow_status()

    if not state:
        release_lock(lock_fd)
        sys.exit(0)

    should_continue, message = get_continuation_message(state)

    if should_continue:
        response = {
            "decision": "block",
            "reason": message
        }
        print(json.dumps(response))

finally:
    release_lock(lock_fd)

sys.exit(0)
