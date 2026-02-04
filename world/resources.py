import random
import uuid
from typing import Dict, List, Optional
from config import WORLD_WIDTH, WORLD_HEIGHT, RESOURCE_REGEN_RATE, RESOURCE_ENERGY_VALUE, INITIAL_RESOURCE_COUNT

class ResourceManager:
    """
    Manages the lifecycle of resources in the world.
    """
    def __init__(self, world_grid: List[List[List[str]]], resources_registry: Dict[str, dict], telemetry=None):
        self.grid = world_grid
        self.registry = resources_registry
        self.telemetry = telemetry
        
    def spawn_initial_resources(self):
        """Populates the world with the initial set of resources."""
        for _ in range(INITIAL_RESOURCE_COUNT):
            self._spawn_random_resource()

    def regen_tick(self):
        """
        Chance to spawn new resources at random locations.
        """
        if random.random() < RESOURCE_REGEN_RATE:
            self._spawn_random_resource()

    def consume_resource(self, resource_id: str) -> int:
        """
        Attempts to consume a resource.
        Returns the energy value if successful, 0 if resource doesn't exist.
        """
        if resource_id in self.registry:
            res = self.registry[resource_id]
            x, y = res['x'], res['y']
            value = res['value']
            
            # Remove from grid and registry
            if resource_id in self.grid[x][y]:
                self.grid[x][y].remove(resource_id)
            
            del self.registry[resource_id]
            
            if self.telemetry:
                self.telemetry.emit("resource_deplete", {"id": resource_id, "x": x, "y": y, "value": value})
            
            return value
        return 0

    def _spawn_random_resource(self):
        x = random.randint(0, WORLD_WIDTH - 1)
        y = random.randint(0, WORLD_HEIGHT - 1)
        
        # Determine unique ID
        res_id = f"res_{uuid.uuid4().hex[:8]}"
        
        self.registry[res_id] = {
            'x': x,
            'y': y,
            'value': RESOURCE_ENERGY_VALUE,
            'type': 'food' 
        }
        self.grid[x][y].append(res_id)
        
        if self.telemetry:
            self.telemetry.emit("resource_spawn", {"id": res_id, "x": x, "y": y, "value": RESOURCE_ENERGY_VALUE})
