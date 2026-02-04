"""
Cosmology Module

Provides the theological ontology layers:
- Laws: Immutable meta-rules (God layer)
- Angels: Non-volitional executors (background machinery)
- Demon: Cognitive perturbator (whisper layer)
- Genesis: Origin creation (Adam & Eve)
"""

from cosmology.laws import COSMIC_LAWS, Laws, validate_action, is_death_final
from cosmology.demon import Demon, DistortionType, Whisper
from cosmology.genesis import create_origin_agents, ADAM_GENOME, EVE_GENOME
from cosmology.angels import Recorder, Provisioner, Terminator

__all__ = [
    "COSMIC_LAWS",
    "Laws", 
    "validate_action",
    "is_death_final",
    "Demon",
    "DistortionType",
    "Whisper",
    "create_origin_agents",
    "ADAM_GENOME",
    "EVE_GENOME",
    "Recorder",
    "Provisioner",
    "Terminator",
]

