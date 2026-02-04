import json
import logging
import time

logger = logging.getLogger(__name__)

class Telemetry:
    """
    Observer pattern implementation.
    Writes events to a JSONL file.
    """
    def __init__(self, log_file: str = "simulation_telemetry.jsonl"):
        self.log_file = log_file
        # Clear existing log
        with open(self.log_file, 'w') as f:
            pass

    def emit(self, event_type: str, details: dict):
        """
        Record an event.
        Non-blocking in principle (OS caching), but synchronous IO here for simplicity.
        """
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Telemetry write failed: {e}")

# Global instance pattern for simplicity if needed, or injected
