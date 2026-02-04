import random
import copy
from typing import Dict, Optional, TYPE_CHECKING
from config import MUTATION_RATE, MUTATION_STRENGTH, CROSSOVER_RATE

# Trait bounds for clamping
TRAIT_BOUNDS = {
    "risk_tolerance": (0.0, 1.0),
    "curiosity": (0.0, 1.0),
    "social_bias": (0.0, 1.0),
    "memory_retention": (0.0, 1.0),
    "metabolism_efficiency": (0.5, 2.0),
    "aggression": (0.0, 1.0),
    "cooperation": (0.0, 1.0),
    "reproduction_threshold": (0.2, 0.8),
    "perception_acuity": (0.5, 1.5),
    "lifespan_factor": (0.8, 1.5),
}


class Genome:
    """
    The genetic blueprint of an agent.
    Determines predispositions and probabilities.
    
    Traits:
    - risk_tolerance: 0=fearful, 1=reckless - affects exploration vs exploitation
    - curiosity: 0=conservative, 1=explorer - affects movement patterns
    - social_bias: 0=hermit, 1=gregarious - affects interactions with other agents
    - memory_retention: 0=forgetful, 1=photographic - affects learning from past
    - metabolism_efficiency: 0.5-2.0 - multiplier on energy cost
    - aggression: 0=passive, 1=aggressive - affects conflict behavior
    - cooperation: 0=selfish, 1=altruistic - affects resource sharing
    - reproduction_threshold: 0.2-0.8 - energy % that triggers reproduction urge
    - perception_acuity: 0.5-1.5 - multiplier on perception radius
    - lifespan_factor: 0.8-1.5 - affects natural lifespan
    """
    
    def __init__(self, genes: Dict[str, float] = None):
        if genes:
            self.genes = genes
        else:
            # Default random initialization with expanded trait set
            self.genes = {
                # Core survival traits
                "risk_tolerance": random.random(),
                "curiosity": random.random(),
                "metabolism_efficiency": random.uniform(0.8, 1.2),
                
                # Social traits
                "social_bias": random.random(),
                "aggression": random.random(),
                "cooperation": random.random(),
                
                # Cognitive traits
                "memory_retention": random.random(),
                "perception_acuity": random.uniform(0.8, 1.2),
                
                # Life history traits
                "reproduction_threshold": random.uniform(0.3, 0.6),
                "lifespan_factor": random.uniform(0.9, 1.1),
            }

    def mutate(self) -> 'Genome':
        """
        Applies random mutations to the genome.
        Returns a NEW Genome instance (this one is immutable-ish).
        """
        new_genes = copy.deepcopy(self.genes)
        
        for trait, value in new_genes.items():
            if random.random() < MUTATION_RATE:
                # Apply mutation with trait-specific bounds
                change = random.uniform(-MUTATION_STRENGTH, MUTATION_STRENGTH)
                bounds = TRAIT_BOUNDS.get(trait, (0.0, 1.0))
                new_value = max(bounds[0], min(bounds[1], value + change))
                new_genes[trait] = new_value
                
        return Genome(new_genes)

    def crossover(self, other: 'Genome') -> 'Genome':
        """
        Sexual reproduction: combine two genomes.
        Uses uniform crossover with per-gene selection from either parent.
        Returns a NEW mutated child Genome.
        """
        child_genes = {}
        
        for trait in self.genes:
            if random.random() < CROSSOVER_RATE:
                # Crossover: pick from one parent or blend
                if random.random() < 0.5:
                    # Discrete selection from one parent
                    child_genes[trait] = random.choice([
                        self.genes[trait], 
                        other.genes.get(trait, self.genes[trait])
                    ])
                else:
                    # Blended inheritance (average with noise)
                    parent1_val = self.genes[trait]
                    parent2_val = other.genes.get(trait, parent1_val)
                    blend_ratio = random.uniform(0.3, 0.7)
                    child_genes[trait] = parent1_val * blend_ratio + parent2_val * (1 - blend_ratio)
            else:
                # No crossover, inherit from primary parent
                child_genes[trait] = self.genes[trait]
        
        # Apply mutation to child
        return Genome(child_genes).mutate()

    def genetic_distance(self, other: 'Genome') -> float:
        """
        Calculate genetic distance between two genomes.
        Useful for studying speciation and diversity.
        """
        distance = 0.0
        count = 0
        for trait in self.genes:
            if trait in other.genes:
                # Normalize by trait bounds
                bounds = TRAIT_BOUNDS.get(trait, (0.0, 1.0))
                range_size = bounds[1] - bounds[0]
                diff = abs(self.genes[trait] - other.genes[trait]) / range_size
                distance += diff
                count += 1
        return distance / count if count > 0 else 0.0

    def get_behavioral_profile(self) -> Dict[str, str]:
        """
        Returns human-readable behavioral tendencies based on genome.
        Useful for LLM prompts and research analysis.
        """
        profile = {}
        
        # Risk assessment
        risk = self.genes.get("risk_tolerance", 0.5)
        if risk > 0.7:
            profile["risk_style"] = "reckless risk-taker"
        elif risk > 0.4:
            profile["risk_style"] = "balanced decision-maker"
        else:
            profile["risk_style"] = "cautious and risk-averse"
        
        # Exploration style
        curiosity = self.genes.get("curiosity", 0.5)
        if curiosity > 0.7:
            profile["exploration"] = "loves exploring new areas"
        elif curiosity > 0.4:
            profile["exploration"] = "occasionally explores"
        else:
            profile["exploration"] = "prefers familiar territory"
        
        # Social style
        social = self.genes.get("social_bias", 0.5)
        aggression = self.genes.get("aggression", 0.5)
        cooperation = self.genes.get("cooperation", 0.5)
        
        if social > 0.6 and cooperation > 0.5:
            profile["social_style"] = "friendly and cooperative"
        elif aggression > 0.6:
            profile["social_style"] = "competitive and territorial"
        elif social < 0.4:
            profile["social_style"] = "solitary loner"
        else:
            profile["social_style"] = "neutral toward others"
        
        # Reproduction drive
        repro_thresh = self.genes.get("reproduction_threshold", 0.5)
        if repro_thresh < 0.35:
            profile["reproduction_drive"] = "strong urge to reproduce early"
        elif repro_thresh > 0.6:
            profile["reproduction_drive"] = "waits for optimal conditions to reproduce"
        else:
            profile["reproduction_drive"] = "moderate reproduction drive"
        
        return profile

    def to_dict(self) -> Dict[str, float]:
        return self.genes.copy()
    
    def __repr__(self) -> str:
        traits = ", ".join(f"{k}={v:.2f}" for k, v in self.genes.items())
        return f"Genome({traits})"
