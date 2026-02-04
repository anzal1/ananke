import uuid
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from agent.genome import Genome
from agent.drives import Drives
from agent.memory import Memory
from agent.cognition import CognitionCore
from config import MAX_ENERGY, INITIAL_ENERGY, TRACK_LINEAGE

logger = logging.getLogger(__name__)


@dataclass
class Lineage:
    """Tracks the evolutionary lineage of an agent."""
    parent_ids: List[str] = field(default_factory=list)  # Can have 1 or 2 parents
    generation: int = 0
    ancestors: List[str] = field(default_factory=list)  # Full ancestor chain (limited depth)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "parent_ids": self.parent_ids,
            "generation": self.generation,
            "ancestors": self.ancestors[:10]  # Limit to 10 most recent ancestors
        }


class Agent:
    """
    The Agent entity.
    Composes all sub-modules.
    
    agent_type can be:
    - "origin": Adam/Eve - the primordial ancestors
    - "descendant": All children and future generations
    """
    def __init__(
        self, 
        agent_id: str = None, 
        genome: Genome = None, 
        parent_ids: List[str] = None,
        agent_type: str = "descendant",
        generation: int = 0,
        ancestors: List[str] = None
    ):
        self.id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type  # "origin" or "descendant"
        
        # Lineage tracking for research
        self.lineage = Lineage(
            parent_ids=parent_ids or [],
            generation=generation,
            ancestors=ancestors or []
        )
        
        # For backward compatibility
        self.parent_id = parent_ids[0] if parent_ids else None
        
        # 1. Genome (Nature)
        self.genome = genome or Genome()
        
        # 2. Body / Drives (Physiology)
        self.drives = Drives(max_energy=MAX_ENERGY)
        self.drives.energy = INITIAL_ENERGY  # Reset to initial if new spawn
        
        # 3. Brain (Cognition)
        self.cognition = CognitionCore()
        self.memory = Memory()
        
        # Life statistics for research
        self.age_ticks = 0
        self.is_alive = True
        self.cause_of_death: Optional[str] = None
        
        # Action tracking for fitness analysis
        self.lifetime_stats = {
            "actions_taken": 0,
            "resources_consumed": 0,
            "energy_gained": 0,
            "energy_spent": 0,
            "children_produced": 0,
            "distance_traveled": 0,
            "demon_whispers_received": 0,
            "demon_whispers_followed": 0,
        }

    async def wake_up_and_act(self, world_view: dict) -> Optional[dict]:
        """
        The main tick function for the agent.
        1. Perceive (passed in world_view)
        2. Internal Update (Drives)
        3. Think (Cognition)
        4. Decide
        """
        if not self.is_alive:
            return None

        self.age_ticks += 1
        
        # Context for the Brain - now includes behavioral profile
        context = {
            "perception": world_view,
            "drives": self.drives.get_state(),
            "memory": self.memory.get_recent_episodes(),
            "genome": self.genome.to_dict(),
            "behavioral_profile": self.genome.get_behavioral_profile(),
            "age": self.age_ticks,
            "generation": self.lineage.generation,
        }
        
        # Call LLM (Async)
        decision = await self.cognition.think(context)
        
        # Track action
        self.lifetime_stats["actions_taken"] += 1
        
        return decision

    def apply_cost(self, cost: int):
        """Apply energy cost and track it."""
        self.drives.energy -= cost
        self.lifetime_stats["energy_spent"] += cost
        if self.drives.energy <= 0:
            self.die("starvation")

    def gain_energy(self, amount: int):
        """Gain energy from consuming resources."""
        self.drives.consume(amount)
        self.lifetime_stats["energy_gained"] += amount
        self.lifetime_stats["resources_consumed"] += 1

    def record_reproduction(self):
        """Track successful reproduction."""
        self.lifetime_stats["children_produced"] += 1
        # Reset reproduction urge after having a child
        self.drives.reproduction_urge = 0.0

    def record_movement(self):
        """Track movement for distance calculations."""
        self.lifetime_stats["distance_traveled"] += 1

    def record_demon_whisper(self, followed: bool = False):
        """Track demon influence for research."""
        self.lifetime_stats["demon_whispers_received"] += 1
        if followed:
            self.lifetime_stats["demon_whispers_followed"] += 1

    def die(self, cause: str):
        """Mark agent as dead with cause."""
        self.is_alive = False
        self.cause_of_death = cause
        logger.info(f"Agent {self.id} (gen {self.lineage.generation}) died of {cause} at age {self.age_ticks}")

    def get_fitness_score(self) -> float:
        """
        Calculate a fitness score for evolutionary analysis.
        Higher is better. Based on survival + reproduction success.
        """
        # Components of fitness:
        # 1. Survival time (logarithmic to prevent runaway)
        survival_score = min(self.age_ticks / 100, 5.0)
        
        # 2. Reproduction success (most important for evolution)
        reproduction_score = self.lifetime_stats["children_produced"] * 2.0
        
        # 3. Resource efficiency
        if self.lifetime_stats["energy_spent"] > 0:
            efficiency = self.lifetime_stats["energy_gained"] / self.lifetime_stats["energy_spent"]
        else:
            efficiency = 0
        efficiency_score = min(efficiency, 2.0)
        
        return survival_score + reproduction_score + efficiency_score

    def get_research_snapshot(self) -> Dict[str, Any]:
        """
        Returns comprehensive data about this agent for research export.
        """
        return {
            "id": self.id,
            "agent_type": self.agent_type,
            "generation": self.lineage.generation,
            "parent_ids": self.lineage.parent_ids,
            "genome": self.genome.to_dict(),
            "behavioral_profile": self.genome.get_behavioral_profile(),
            "is_alive": self.is_alive,
            "age_ticks": self.age_ticks,
            "cause_of_death": self.cause_of_death,
            "lifetime_stats": self.lifetime_stats,
            "fitness_score": self.get_fitness_score(),
            "current_energy": self.drives.energy if self.is_alive else 0,
        }

    def __repr__(self) -> str:
        status = "alive" if self.is_alive else f"dead({self.cause_of_death})"
        return f"Agent({self.id}, gen={self.lineage.generation}, age={self.age_ticks}, {status})"
