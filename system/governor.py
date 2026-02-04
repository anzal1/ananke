from config import MAX_AGENTS, SIMULATION_TIMEOUT_TICKS

class Governor:
    """
    Safety / Control Boundaries.
    Enforces meta-rules that the system cannot violate.
    """
    def __init__(self, runtime):
        self.runtime = runtime

    def check_bounds(self):
        """
        Runs safety checks.
        """
        # 1. Population Control
        if len(self.runtime.agents) > MAX_AGENTS:
            self._cull_population()

        # 2. Time Logic (handled by main loop break condition generally, but checked here)
        if self.runtime.tick_count >= SIMULATION_TIMEOUT_TICKS:
            return False # Stop signal
            
        return True

    def _cull_population(self):
        """
        If population exceeds max, remove oldest/weakest to maintain stability.
        Crucial for preventing infinite loops/crashes.
        """
        # Sort by energy (weakest first)
        agents_sorted = sorted(self.runtime.agents, key=lambda a: a.drives.energy)
        
        # Remove excess
        excess = len(self.runtime.agents) - MAX_AGENTS
        for i in range(excess):
            agent_to_kill = agents_sorted[i]
            self.runtime.kill_agent(agent_to_kill, "governor_cull")
