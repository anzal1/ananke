from typing import List, Dict, Any
import collections
import time

class Memory:
    """
    Agent's internal memory.
    V1: Simple list of recent events (Episodic).
    V2: Vector store for Semantic memory.
    """
    def __init__(self, capacity: int = 50):
        self.episodic_buffer = collections.deque(maxlen=capacity)
        self.reflection_summary = "" # Consolidated long-term memory summary

    def add_event(self, event_description: str, metadata: Dict[str, Any] = None):
        """
        Logs a specific event.
        """
        timestamp = time.time()
        entry = {
            "time": timestamp,
            "desc": event_description,
            "meta": metadata or {}
        }
        self.episodic_buffer.append(entry)

    def get_recent_episodes(self, limit: int = 5) -> List[str]:
        """
        Returns recent 'raw' memories for the context window.
        """
        # Get last N items
        items = list(self.episodic_buffer)[-limit:]
        return [f"{item['desc']}" for item in items]

    def consolidate(self, reflection: str):
        """
        Called when agents 'reflect' to compress episodic memory into semantic/summary.
        """
        self.reflection_summary = reflection
        # In a real system, we might clear episodic buffer or move it to long-term storage
