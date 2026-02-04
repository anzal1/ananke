"""
Genesis Module

Handles the creation of origin agents (Adam & Eve).
These are the primordial ancestors from which all other agents descend.
"""

import logging
from typing import Tuple
from agent.core import Agent
from agent.genome import Genome

logger = logging.getLogger(__name__)


# Fixed origin genomes - not random, but balanced
ADAM_GENOME = Genome(genes={
    "risk_tolerance": 0.5,
    "curiosity": 0.7,
    "social_bias": 0.6,
    "memory_retention": 1.0,  # Perfect memory for origin agents
    "metabolism_efficiency": 1.0,
})

EVE_GENOME = Genome(genes={
    "risk_tolerance": 0.4,
    "curiosity": 0.8,
    "social_bias": 0.7,
    "memory_retention": 1.0,  # Perfect memory for origin agents
    "metabolism_efficiency": 1.0,
})


def create_origin_agents() -> Tuple[Agent, Agent]:
    """
    Creates Adam and Eve - the origin ancestors.
    
    These agents are special:
    - Named (not UUID)
    - Full cognition
    - Perfect memory retention
    - No parent lineage
    - agent_type = "origin"
    """
    adam = Agent(
        agent_id="adam",
        genome=ADAM_GENOME,
        parent_id=None,
        agent_type="origin"
    )
    
    eve = Agent(
        agent_id="eve", 
        genome=EVE_GENOME,
        parent_id=None,
        agent_type="origin"
    )
    
    logger.info("Genesis complete: Adam and Eve created")
    
    return adam, eve
