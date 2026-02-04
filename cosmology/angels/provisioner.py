"""
Provisioner Angel

Resource spawn engine.
Distributes resources according to probability distributions.

No favoritism. No intention. Pure function.
"""

import random
import uuid
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class Provisioner:
    """
    The Provisioner Angel - Resource distribution engine.
    
    Spawns resources according to configured probability distributions.
    No will, no decision - just execution of spawn rules.
    """
    
    def __init__(
        self,
        world_grid: List[List[List[str]]],
        resources_registry: Dict[str, dict],
        recorder: Optional[Any] = None,
        spawn_probability: float = 0.05,
        resource_value: int = 20,
        world_width: int = 100,
        world_height: int = 100
    ):
        self.grid = world_grid
        self.registry = resources_registry
        self.recorder = recorder
        self.spawn_probability = spawn_probability
        self.resource_value = resource_value
        self.world_width = world_width
        self.world_height = world_height
    
    def provision_initial(self, count: int):
        """
        Provision the initial resources at world creation.
        """
        for _ in range(count):
            self._spawn_resource()
        
        logger.info(f"Provisioner: Initial provision of {count} resources complete")
    
    def provision_tick(self):
        """
        Called each tick to potentially spawn new resources.
        Follows probability distribution - no favoritism.
        """
        if random.random() < self.spawn_probability:
            self._spawn_resource()
    
    def _spawn_resource(self) -> Optional[str]:
        """
        Spawn a single resource at a random location.
        Returns the resource ID if spawned, None otherwise.
        """
        x = random.randint(0, self.world_width - 1)
        y = random.randint(0, self.world_height - 1)
        
        res_id = f"res_{uuid.uuid4().hex[:8]}"
        
        self.registry[res_id] = {
            'x': x,
            'y': y,
            'value': self.resource_value,
            'type': 'food'
        }
        self.grid[x][y].append(res_id)
        
        if self.recorder:
            self.recorder.record("resource_spawn", {
                "id": res_id,
                "x": x,
                "y": y,
                "value": self.resource_value
            })
        
        return res_id
    
    def consume_resource(self, resource_id: str) -> int:
        """
        Consume a resource and return its energy value.
        """
        if resource_id not in self.registry:
            return 0
        
        res = self.registry[resource_id]
        x, y = res['x'], res['y']
        value = res['value']
        
        # Remove from grid and registry
        if resource_id in self.grid[x][y]:
            self.grid[x][y].remove(resource_id)
        
        del self.registry[resource_id]
        
        if self.recorder:
            self.recorder.record("resource_deplete", {
                "id": resource_id,
                "x": x,
                "y": y,
                "value": value
            })
        
        return value
