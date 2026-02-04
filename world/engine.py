import random
import logging
from typing import Dict, List, Tuple, Optional
from config import WORLD_WIDTH, WORLD_HEIGHT

logger = logging.getLogger(__name__)

class World:
    """
    The Simulation World. 
    Manages the grid, time, resources, and acts as the source of truth for physical reality.
    """
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.tick_count = 0
        
        # Grid to store entity IDs (Agent ID or Resource ID)
        # Usage: self.grid[x][y] = list of things at that location
        self.grid: List[List[List[str]]] = [[[] for _ in range(self.height)] for _ in range(self.width)]
        
        self.agents: Dict[str, dict] = {} # Map agent_id -> minimal physical state (x, y)
        self.resources: Dict[str, dict] = {} # Map resource_id -> {x, y, value}

    def add_agent(self, agent_id: str, x: int, y: int):
        """Places an agent in the world."""
        if not self.is_valid_position(x, y):
            raise ValueError(f"Invalid position {x}, {y}")
        
        self.agents[agent_id] = {'x': x, 'y': y}
        self.grid[x][y].append(agent_id)
        logger.info(f"Agent {agent_id} added at ({x}, {y})")

    def remove_agent(self, agent_id: str):
        """Removes an agent from the world (Death)."""
        if agent_id in self.agents:
            pos = self.agents[agent_id]
            self.grid[pos['x']][pos['y']].remove(agent_id)
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} removed from world.")

    def move_agent(self, agent_id: str, dx: int, dy: int) -> bool:
        """
        Attempts to move an agent by delta (dx, dy).
        Returns True if successful, False if blocked/invalid.
        """
        if agent_id not in self.agents:
            return False
            
        current_pos = self.agents[agent_id]
        new_x = current_pos['x'] + dx
        new_y = current_pos['y'] + dy
        
        if self.is_valid_position(new_x, new_y):
            # Update Grid
            self.grid[current_pos['x']][current_pos['y']].remove(agent_id)
            self.grid[new_x][new_y].append(agent_id)
            
            # Update State
            self.agents[agent_id]['x'] = new_x
            self.agents[agent_id]['y'] = new_y
            return True
        
        return False

    def is_valid_position(self, x: int, y: int) -> bool:
        """Checks if a position is within the world bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_surroundings(self, agent_id: str, radius: int) -> dict:
        """
        Returns a snapshot of the world around the agent.
        Partial observability implementation.
        """
        if agent_id not in self.agents:
            return {}
            
        pos = self.agents[agent_id]
        cx, cy = pos['x'], pos['y']
        
        visible_area = {}
        
        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - radius, cy + radius + 1):
                if self.is_valid_position(x, y):
                    # Only include non-empty cells to save tokens/memory
                    if self.grid[x][y]: 
                        # We might filter what agents can see about other agents here
                        # For now, just return specific IDs
                        visible_area[f"{x},{y}"] = self.grid[x][y]
                        
        return {
            "my_position": {"x": cx, "y": cy},
            "visible_grid": visible_area,
            "world_size": {"w": self.width, "h": self.height}
        }

    def tick(self):
        """Advances the world time by one unit."""
        self.tick_count += 1
        # TODO: Trigger resource regeneration here
