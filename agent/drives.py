class Drives:
    """
    Manages the internal biological drives of the agent.
    Inputs to the Cognition Core.
    """
    def __init__(self, max_energy: int):
        self.energy = max_energy
        self.max_energy = max_energy
        
        # Drive values: 0 = Satisfied, 1 = Urgent
        self.hunger = 0.0
        self.reproduction_urge = 0.0
        self.social_need = 0.0

    def update(self, energy_change: int, genome_bias: dict):
        """
        Updates drives based on energy flux and genome ticks.
        """
        # Energy directly maps to hunger
        self.energy = max(0, min(self.max_energy, self.energy + energy_change))
        self.hunger = 1.0 - (self.energy / self.max_energy)
        
        # Reproduction urge grows over time (abstract biological clock), modulated by genome?
        # For simplicity, just grow linearly
        self.reproduction_urge = min(1.0, self.reproduction_urge + 0.01)
        
        # Social need might be static or dynamic
        # Ignored for V1

    def get_state(self) -> dict:
        return {
            "energy": self.energy,
            "max_energy": self.max_energy,
            "hunger": round(self.hunger, 2),
            "reproduction_urge": round(self.reproduction_urge, 2)
        }
    
    def consume(self, amount: int):
        self.energy = min(self.max_energy, self.energy + amount)
