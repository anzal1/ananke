import asyncio
import logging
import random
from typing import List, Optional, Tuple

from world.engine import World
from world.rules import InteractionRules
from agent.core import Agent
from agent.genome import Genome

# Cosmology imports
from cosmology.angels import Recorder, Provisioner, Terminator
from cosmology.demon import Demon
from cosmology.genesis import create_origin_agents
from cosmology.laws import COSMIC_LAWS, is_death_final

# Research metrics
from system.research_metrics import ResearchMetrics

from config import (
    TICK_DURATION_SEC, MAX_AGENTS, MUTATION_RATE,
    WORLD_WIDTH, WORLD_HEIGHT, RESOURCE_REGEN_RATE,
    RESOURCE_ENERGY_VALUE, INITIAL_RESOURCE_COUNT,
    DEMON_INFLUENCE_PROBABILITY, SEXUAL_REPRODUCTION,
    MATING_RADIUS, REPRODUCTION_COST, MIN_REPRODUCTION_ENERGY,
    EXPORT_METRICS_INTERVAL, TRACK_LINEAGE
)

logger = logging.getLogger(__name__)


class Runtime:
    """
    The simulation runtime that orchestrates all components.
    
    Integrates:
    - World: Physical reality
    - Agents: Biological entities
    - Angels: Background machinery (Recorder, Provisioner, Terminator)
    - Demon: Cognitive perturbator
    - Research Metrics: Data collection for analysis
    """
    
    def __init__(self, seed: int = None):
        self.world = World()
        
        # Initialize Angel subsystems
        # Write to observatory public folder for live visualization
        self.recorder = Recorder(log_file="tools/observatory/public/divine_ledger.jsonl")
        self.provisioner = Provisioner(
            world_grid=self.world.grid,
            resources_registry=self.world.resources,
            recorder=self.recorder,
            spawn_probability=RESOURCE_REGEN_RATE,
            resource_value=RESOURCE_ENERGY_VALUE,
            world_width=WORLD_WIDTH,
            world_height=WORLD_HEIGHT
        )
        self.terminator = Terminator(recorder=self.recorder)
        
        # Initialize Demon
        self.demon = Demon(
            influence_probability=DEMON_INFLUENCE_PROBABILITY,
            recorder=self.recorder
        )
        
        # Initialize Research Metrics
        self.metrics = ResearchMetrics()
        if seed is not None:
            self.metrics.set_seed(seed)
        
        self.agents: List[Agent] = []
        self.tick_count = 0
        
        # Track agents looking for mates (for sexual reproduction)
        self._pending_reproductions: List[Tuple[Agent, Optional[Agent]]] = []

    def spawn_origin_agents(self):
        """
        Creates Adam and Eve - the origin ancestors.
        Uses Genesis to create specially configured agents.
        """
        adam, eve = create_origin_agents()
        
        # Place Adam
        adam_x, adam_y = self.world.width // 2 - 5, self.world.height // 2
        self.agents.append(adam)
        self.world.add_agent(adam.id, adam_x, adam_y)
        self.recorder.record_birth(
            agent_id=adam.id,
            parent_id=None,
            agent_type="origin",
            position=(adam_x, adam_y),
            genome=adam.genome.to_dict()
        )
        self.metrics.record_birth(adam)
        
        # Place Eve
        eve_x, eve_y = self.world.width // 2 + 5, self.world.height // 2
        self.agents.append(eve)
        self.world.add_agent(eve.id, eve_x, eve_y)
        self.recorder.record_birth(
            agent_id=eve.id,
            parent_id=None,
            agent_type="origin",
            position=(eve_x, eve_y),
            genome=eve.genome.to_dict()
        )
        self.metrics.record_birth(eve)
        
        logger.info(f"Genesis complete: Adam at ({adam_x}, {adam_y}), Eve at ({eve_x}, {eve_y})")

    def spawn_agent(
        self, 
        x: int = None, 
        y: int = None, 
        genome: Genome = None, 
        parent_ids: List[str] = None,
        generation: int = 1,
        ancestors: List[str] = None
    ) -> Optional[Agent]:
        """
        Creates and places a new descendant agent.
        Supports both single-parent and two-parent reproduction.
        """
        if len(self.agents) >= MAX_AGENTS:
            logger.warning("Max agents reached, cannot spawn.")
            return None

        x = x if x is not None else random.randint(0, self.world.width - 1)
        y = y if y is not None else random.randint(0, self.world.height - 1)
        
        # Ensure valid spawn
        attempts = 0
        while not self.world.is_valid_position(x, y) and attempts < 10:
            x = random.randint(0, self.world.width - 1)
            y = random.randint(0, self.world.height - 1)
            attempts += 1
        
        # Build ancestor list for lineage tracking
        if ancestors is None:
            ancestors = []
        if parent_ids:
            ancestors = parent_ids + ancestors[:8]  # Keep last 10 ancestors total
            
        new_agent = Agent(
            genome=genome, 
            parent_ids=parent_ids,
            agent_type="descendant",
            generation=generation,
            ancestors=ancestors
        )
        self.agents.append(new_agent)
        self.world.add_agent(new_agent.id, x, y)
        
        # Record via Recorder angel
        self.recorder.record_birth(
            agent_id=new_agent.id,
            parent_id=parent_ids[0] if parent_ids else None,
            agent_type="descendant",
            position=(x, y),
            genome=new_agent.genome.to_dict()
        )
        
        # Record for research metrics
        self.metrics.record_birth(new_agent, parent_ids)
        
        return new_agent
    
    def find_nearby_mate(self, agent: Agent) -> Optional[Agent]:
        """
        Find a potential mate near the agent for sexual reproduction.
        Returns None if no suitable mate is found.
        """
        if agent.id not in self.world.agents:
            return None
            
        pos = self.world.agents[agent.id]
        agent_x, agent_y = pos['x'], pos['y']
        
        # Find other agents within mating radius
        candidates = []
        for other in self.agents:
            if other.id == agent.id or not other.is_alive:
                continue
            if other.id not in self.world.agents:
                continue
                
            other_pos = self.world.agents[other.id]
            distance = abs(other_pos['x'] - agent_x) + abs(other_pos['y'] - agent_y)
            
            if distance <= MATING_RADIUS:
                # Check if other agent has enough energy to contribute
                if other.drives.energy > MIN_REPRODUCTION_ENERGY / 2:
                    candidates.append((other, distance))
        
        if not candidates:
            return None
        
        # Prefer closer mates
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
    
    def reproduce_agents(self, parent1: Agent, parent2: Optional[Agent] = None) -> Optional[Agent]:
        """
        Handle reproduction between one or two agents.
        If parent2 is provided, uses sexual reproduction (crossover).
        Otherwise uses asexual reproduction (mutation only).
        """
        if parent1.drives.energy < MIN_REPRODUCTION_ENERGY:
            return None
            
        pos = self.world.agents.get(parent1.id)
        if not pos:
            return None
        
        # Determine reproduction type
        if parent2 and SEXUAL_REPRODUCTION:
            # Sexual reproduction with crossover
            child_genome = parent1.genome.crossover(parent2.genome)
            parent_ids = [parent1.id, parent2.id]
            generation = max(parent1.lineage.generation, parent2.lineage.generation) + 1
            ancestors = parent1.lineage.ancestors + parent2.lineage.ancestors
            
            # Both parents pay cost
            parent1.apply_cost(REPRODUCTION_COST // 2)
            parent2.apply_cost(REPRODUCTION_COST // 2)
            parent1.record_reproduction()
            parent2.record_reproduction()
            
            logger.info(f"Sexual reproduction: {parent1.id} + {parent2.id} (gen {generation})")
        else:
            # Asexual reproduction
            child_genome = parent1.genome.mutate()
            parent_ids = [parent1.id]
            generation = parent1.lineage.generation + 1
            ancestors = parent1.lineage.ancestors
            
            parent1.apply_cost(REPRODUCTION_COST)
            parent1.record_reproduction()
            
            logger.info(f"Asexual reproduction: {parent1.id} (gen {generation})")
        
        # Spawn child near parent
        child = self.spawn_agent(
            x=pos['x'], 
            y=pos['y'], 
            genome=child_genome, 
            parent_ids=parent_ids,
            generation=generation,
            ancestors=ancestors
        )
        
        return child

    def kill_agent(self, agent: Agent, cause: str):
        """Removes agent from simulation via Terminator angel."""
        if agent.id not in self.world.agents:
            return
            
        pos = self.world.agents[agent.id]
        
        # Record death in research metrics BEFORE cleanup
        self.metrics.record_death(agent, cause)
        
        # Use Terminator angel for death
        def cleanup(a):
            self.world.remove_agent(a.id)
            if a in self.agents:
                self.agents.remove(a)
        
        self.terminator.execute(
            agent=agent,
            cause=cause,
            world_position=(pos['x'], pos['y']),
            on_death_callback=cleanup
        )

    async def step(self):
        """
        One global simulation tick.
        """
        self.tick_count += 1
        logger.info(f"--- TICK {self.tick_count} ---")
        
        # 1. World Updates (via Provisioner angel)
        self.provisioner.provision_tick()
        
        # 2. Collect Agent Decisions (Concurrent)
        async def get_agent_decision(agent):
            if not agent.is_alive:
                return None
            
            # Get perception from world
            view = self.world.get_surroundings(agent.id, radius=5)
            
            # DEMON LAYER: Potentially distort perception before cognition
            distorted_view, whisper = self.demon.maybe_distort(
                agent_id=agent.id,
                perception=view,
                drives=agent.drives.get_state()
            )
            
            # Track demon whisper in agent stats
            if whisper:
                agent.record_demon_whisper(followed=False)  # We'll update if followed later
            
            # Agent thinks with potentially distorted perception
            decision = await agent.wake_up_and_act(distorted_view)
            return (agent, decision, whisper)

        results = await asyncio.gather(*[get_agent_decision(a) for a in self.agents])
        
        # 3. Resolve Actions (random order to avoid bias)
        random.shuffle(results)
        
        for item in results:
            if not item:
                continue
            agent, decision, whisper = item
            if not decision:
                continue
            
            await self._execute_action(agent, decision, whisper)
            
            # Post-action metabolism
            agent.drives.update(-InteractionRules.get_metabolism_cost(agent), agent.genome.to_dict())
            
            # Check death via Terminator
            death_cause = self.terminator.check_death_conditions(agent)
            if death_cause and is_death_final():
                self.kill_agent(agent, death_cause)
        
        # 4. Record population snapshot for research (every tick)
        self.metrics.record_population_snapshot(self.tick_count, self.agents)
        
        # 5. Periodic metrics export
        if self.tick_count % EXPORT_METRICS_INTERVAL == 0:
            logger.info(f"Tick {self.tick_count}: Pop={len([a for a in self.agents if a.is_alive])}, "
                       f"Births={self.metrics.total_births}, Deaths={self.metrics.total_deaths}")

    async def _execute_action(self, agent: Agent, decision: dict, whisper=None):
        """
        Applies the agent's decision to the world.
        Now supports sexual reproduction and tracks demon influence.
        """
        action_type = decision.get("action_type")
        params = decision.get("action_params", {})
        
        cost = 0
        success = False
        outcome_desc = ""
        
        if action_type == "move":
            dx = params.get("dx", 0)
            dy = params.get("dy", 0)
            
            # Enforce unit movement
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            
            cost = InteractionRules.get_movement_cost(agent, dx, dy)
            if agent.drives.energy > cost:
                success = self.world.move_agent(agent.id, dx, dy)
                if success:
                    agent.record_movement()
                    outcome_desc = f"Moved to {self.world.agents[agent.id]['x']}, {self.world.agents[agent.id]['y']}"
                else:
                    outcome_desc = "Move blocked"
            else:
                outcome_desc = "Not enough energy to move"

        elif action_type == "consume":
            pos = self.world.agents[agent.id]
            cell_items = self.world.grid[pos['x']][pos['y']]
            
            # Find a resource
            target_res = None
            for item in cell_items:
                if item.startswith("res_"):
                    target_res = item
                    break
            
            if target_res:
                value = self.provisioner.consume_resource(target_res)
                agent.gain_energy(value)
                success = True
                outcome_desc = f"Ate resource for {value} energy"
            else:
                outcome_desc = "Nothing to eat here"
                
        elif action_type == "reproduce":
            # Try to find a mate for sexual reproduction
            mate = self.find_nearby_mate(agent) if SEXUAL_REPRODUCTION else None
            
            if agent.drives.energy > MIN_REPRODUCTION_ENERGY:
                child = self.reproduce_agents(agent, mate)
                if child:
                    success = True
                    if mate:
                        outcome_desc = f"Reproduced with {mate.id}, child: {child.id} (gen {child.lineage.generation})"
                    else:
                        outcome_desc = f"Reproduced asexually, child: {child.id} (gen {child.lineage.generation})"
                else:
                    outcome_desc = "Reproduction failed"
            else:
                outcome_desc = f"Too weak to reproduce (need {MIN_REPRODUCTION_ENERGY} energy)"
                
        elif action_type == "wait":
            cost = 0
            success = True
            outcome_desc = "Waited"
            
        else:
            outcome_desc = f"Unknown action {action_type}"

        # Apply action cost
        agent.apply_cost(cost)
        
        # Memory update
        agent.memory.add_event(f"Action: {action_type}. Outcome: {outcome_desc}")
        
        # Track if demon whisper was followed
        if whisper:
            # Simplified heuristic: if the action matches the demon's suggestion type
            was_followed = self._check_whisper_followed(whisper, action_type, outcome_desc)
            if was_followed:
                agent.lifetime_stats["demon_whispers_followed"] += 1
                self.metrics.record_demon_whisper(
                    agent_id=agent.id,
                    whisper_type=str(whisper.distortion_type.value) if hasattr(whisper, 'distortion_type') else "unknown",
                    suggestion=str(whisper.distorted_value) if hasattr(whisper, 'distorted_value') else "",
                    action_taken=action_type,
                    was_followed=True
                )
        
        # Record via Recorder angel
        pos = self.world.agents.get(agent.id, {'x': 0, 'y': 0})
        self.recorder.record_action(
            agent_id=agent.id,
            action=action_type,
            outcome=outcome_desc,
            energy=agent.drives.energy,
            position=(pos['x'], pos['y'])
        )

    def _check_whisper_followed(self, whisper, action_type: str, outcome: str) -> bool:
        """
        Heuristic to determine if the agent followed the demon's suggestion.
        """
        if not whisper or not hasattr(whisper, 'distortion_type'):
            return False
        
        whisper_type = whisper.distortion_type.value if hasattr(whisper.distortion_type, 'value') else str(whisper.distortion_type)
        
        # Map distortion types to expected actions
        if whisper_type == "reward_inflation" and action_type == "reproduce":
            return True
        if whisper_type == "risk_minimization" and action_type == "wait":
            return True
        if whisper_type == "scarcity_panic" and action_type == "consume":
            return True
        if whisper_type == "false_urgency" and action_type in ["move", "reproduce"]:
            return True
        
        return False
    
    def export_research_data(self, prefix: str = "simulation"):
        """Export all collected research metrics."""
        self.metrics.export_all(prefix)
        logger.info("Research data exported successfully")
