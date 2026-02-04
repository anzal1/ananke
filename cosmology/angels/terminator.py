"""
Terminator Angel

Death finalization executor.
Executes death when conditions are met.

No mercy. No delay. Pure function.
"""

import logging
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)


class Terminator:
    """
    The Terminator Angel - Death executor.
    
    When an agent's life conditions fail, this angel finalizes death.
    No will, no mercy, no delay - just execution.
    """
    
    def __init__(self, recorder: Optional[Any] = None):
        self.recorder = recorder
        self._death_count = 0
    
    def check_death_conditions(self, agent: Any) -> Optional[str]:
        """
        Check if an agent should die.
        
        Returns the cause of death if conditions are met, None otherwise.
        """
        # Starvation: energy depleted
        if agent.drives.energy <= 0:
            return "starvation"
        
        # Add other death conditions here as needed
        # - Old age
        # - Disease
        # - Combat
        
        return None
    
    def execute(
        self,
        agent: Any,
        cause: str,
        world_position: tuple,
        on_death_callback: Optional[Callable] = None
    ) -> bool:
        """
        Execute the death of an agent.
        
        This is irreversible under cosmic law.
        Returns True if death was executed.
        """
        if not agent.is_alive:
            return False  # Already dead
        
        self._death_count += 1
        
        # Record to the ledger before death
        if self.recorder:
            self.recorder.record_death(
                agent_id=agent.id,
                cause=cause,
                age=agent.age_ticks,
                final_energy=agent.drives.energy,
                position=world_position
            )
        
        # Finalize death on the agent
        agent.is_alive = False
        
        logger.info(f"Terminator: Agent {agent.id} has perished. Cause: {cause}")
        
        # Execute callback for world cleanup
        if on_death_callback:
            on_death_callback(agent)
        
        return True
    
    @property
    def total_deaths(self) -> int:
        """Total number of deaths executed."""
        return self._death_count
