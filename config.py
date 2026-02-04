"""
Global configuration for the Ananke artificial life simulation.
"""
import random
import numpy as np

# ============================================================================
# RESEARCH REPRODUCIBILITY
# ============================================================================
# Set to None for random seed, or a specific integer for reproducible runs
RANDOM_SEED = None  # e.g., 42 for reproducible experiments

def initialize_seed(seed=None):
    """Initialize all random generators with a seed for reproducibility."""
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    random.seed(seed)
    np.random.seed(seed)
    return seed

# ============================================================================
# WORLD DIMENSIONS & TIME
# ============================================================================
WORLD_WIDTH = 100
WORLD_HEIGHT = 100
TICK_DURATION_SEC = 0.5  # Real-time duration of one simulation tick (if running in real-time mode)

# Initial Resources
INITIAL_RESOURCE_COUNT = 50
RESOURCE_REGEN_RATE = 0.05  # Probability of new resource spawning per tick per cell
RESOURCE_ENERGY_VALUE = 20

# Agent Defaults
INITIAL_POPULATION = 5
INITIAL_ENERGY = 100
MAX_ENERGY = 200
METABOLISM_COST = 1  # Energy cost per tick just to exist
MOVE_COST = 2
PERCEPTION_RADIUS = 5

# Genetics
MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.05
CROSSOVER_RATE = 0.7  # Probability of gene crossover vs single-parent inheritance
SEXUAL_REPRODUCTION = True  # Enable two-parent reproduction when possible

# Reproduction
REPRODUCTION_COST = 30
MIN_REPRODUCTION_ENERGY = 40
MATING_RADIUS = 3  # How close agents need to be to mate

# LLM Configuration
LLM_MODEL_NAME = "gemini-2.5-pro"  # Or another suitable model
TEMPERATURE = 0.7

# Safe Guards
MAX_AGENTS = 50
MAX_GENERATIONS = 10
SIMULATION_TIMEOUT_TICKS = 1000

# Cosmology / Theological Ontology
DEMON_INFLUENCE_PROBABILITY = 0.3  # Probability of demon whisper per agent per tick

# ============================================================================
# RESEARCH & ANALYTICS
# ============================================================================
TRACK_LINEAGE = True  # Track full ancestry tree
EXPORT_METRICS_INTERVAL = 100  # Export research metrics every N ticks
METRICS_OUTPUT_DIR = "research_data"  # Directory for research exports

