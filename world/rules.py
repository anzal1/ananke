from config import MOVE_COST, METABOLISM_COST

class InteractionRules:
    """
    Defines the physics and costs of the world.
    Acts as a centralized place to tweak balance.
    """
    
    @staticmethod
    def get_movement_cost(agent, dx: int, dy: int) -> int:
        """
        Calculates energy cost for movement.
        Could be expanded to account for terrain, mass, etc.
        """
        # Cheaper to stay still?
        if dx == 0 and dy == 0:
            return 0
        return MOVE_COST

    @staticmethod
    def get_metabolism_cost(agent) -> int:
        """
        Base cost of existing per tick.
        """
        return METABOLISM_COST

    @staticmethod
    def can_agent_enter(world, x: int, y: int) -> bool:
        """
        Checking if a target cell is valid for entry.
        """
        if not world.is_valid_position(x, y):
            return False
            
        # Example rule: Cannot stack agents
        cell_contents = world.grid[x][y]
        for item in cell_contents:
            if item.startswith("agent_"): # Basic collision
                return False
                
        return True
