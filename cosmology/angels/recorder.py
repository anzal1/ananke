"""
Recorder Angel

Append-only action ledger.
Records all events immutably - nothing can be erased.

This wraps Telemetry with the guarantee that:
- No event can be deleted
- No event can be modified
- All events are timestamped
"""

import json
import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Recorder:
    """
    The Recording Angel - Append-only immutable ledger.
    
    All actions are recorded for accountability.
    This is a pure function executor - no will, no decision.
    """
    
    def __init__(self, log_file: str = "divine_ledger.jsonl"):
        self.log_file = log_file
        self._event_count = 0
        
        # Initialize fresh ledger
        with open(self.log_file, 'w') as f:
            # Write header event
            header = {
                "sequence": 0,
                "timestamp": time.time(),
                "type": "ledger_initialized",
                "details": {"message": "The Recording Angel has begun inscribing"}
            }
            f.write(json.dumps(header) + "\n")
    
    def record(self, event_type: str, details: Dict[str, Any]) -> int:
        """
        Record an event to the immutable ledger.
        
        Returns the sequence number of the recorded event.
        """
        self._event_count += 1
        
        event = {
            "sequence": self._event_count,
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Recorder failed to inscribe: {e}")
            
        return self._event_count
    
    def record_action(self, agent_id: str, action: str, outcome: str, energy: int, position: tuple):
        """Record an agent action."""
        self.record("agent_action", {
            "agent_id": agent_id,
            "action": action,
            "outcome": outcome,
            "energy_after": energy,
            "position": {"x": position[0], "y": position[1]}
        })
    
    def record_birth(self, agent_id: str, parent_id: str, agent_type: str, position: tuple, genome: dict):
        """Record an agent birth/spawn."""
        self.record("agent_birth", {
            "agent_id": agent_id,
            "parent_id": parent_id,
            "agent_type": agent_type,
            "position": {"x": position[0], "y": position[1]},
            "genome": genome
        })
    
    def record_death(self, agent_id: str, cause: str, age: int, final_energy: int, position: tuple):
        """Record an agent death."""
        self.record("agent_death", {
            "agent_id": agent_id,
            "cause": cause,
            "age": age,
            "final_energy": final_energy,
            "position": {"x": position[0], "y": position[1]}
        })
    
    def record_whisper(self, agent_id: str, distortion_type: str, original: str, distorted: str):
        """Record a demon whisper event."""
        self.record("demon_whisper", {
            "agent_id": agent_id,
            "distortion_type": distortion_type,
            "original_perception": original,
            "distorted_perception": distorted
        })
