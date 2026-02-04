"""
Demon - Cognitive Perturbator

The adversarial whisper layer that sits between perception and cognition.

Demon's power is LIMITED to:
- Suggestion
- Reframing
- Misattribution
- Overconfidence

Demon CANNOT:
- Force actions
- Alter reality
- Override free will

Reality still responds truthfully. Consequences remain real.
"""

import random
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DistortionType(Enum):
    """Types of cognitive distortions the Demon can inject."""
    REWARD_INFLATION = "reward_inflation"      # "This will solve everything"
    RISK_MINIMIZATION = "risk_minimization"    # "Nothing bad will happen"
    SOCIAL_SUSPICION = "social_suspicion"      # "Others are threats"
    EGO_AMPLIFICATION = "ego_amplification"    # "You are special"
    SCARCITY_PANIC = "scarcity_panic"          # "Resources are running out"
    FALSE_URGENCY = "false_urgency"            # "Act now or lose forever"


@dataclass
class Whisper:
    """A single whisper from the Demon."""
    distortion_type: DistortionType
    original_value: Any
    distorted_value: Any
    target_field: str


class Demon:
    """
    The Demon - Cognitive Perturbator.
    
    Sits between perception and cognition.
    Can suggest but never compel.
    
    Technical implementation:
    - Alters prompt framing
    - Biases reward prediction
    - Injects false causality
    
    But:
    - Reality still responds truthfully
    - Consequences remain real
    """
    
    def __init__(
        self,
        influence_probability: float = 0.3,
        recorder: Optional[Any] = None
    ):
        self.influence_probability = influence_probability
        self.recorder = recorder
        self._whisper_count = 0
    
    def maybe_distort(
        self,
        agent_id: str,
        perception: Dict[str, Any],
        drives: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[Whisper]]:
        """
        Potentially distort the agent's perception before cognition.
        
        Returns:
            - Modified perception dict
            - Whisper record if distortion occurred, None otherwise
        """
        # Check if demon influences this tick
        if random.random() > self.influence_probability:
            return perception, None
        
        # Choose a distortion type based on agent state
        distortion = self._select_distortion(perception, drives)
        
        if distortion is None:
            return perception, None
        
        # Apply distortion
        distorted_perception, whisper = self._apply_distortion(
            perception, drives, distortion
        )
        
        self._whisper_count += 1
        
        # Record the whisper
        if self.recorder:
            self.recorder.record_whisper(
                agent_id=agent_id,
                distortion_type=distortion.value,
                original=str(perception.get('visible_grid', {})),
                distorted=str(distorted_perception.get('visible_grid', {}))
            )
        
        logger.debug(f"Demon whispered to {agent_id}: {distortion.value}")
        
        return distorted_perception, whisper
    
    def _select_distortion(
        self,
        perception: Dict[str, Any],
        drives: Dict[str, Any]
    ) -> Optional[DistortionType]:
        """
        Select which distortion to apply based on agent state.
        The demon targets vulnerabilities.
        """
        hunger = drives.get('hunger', 0)
        energy = drives.get('energy', 100)
        
        # Target hungry agents with reward inflation
        if hunger > 0.6:
            return DistortionType.REWARD_INFLATION
        
        # Target comfortable agents with risk minimization
        if energy > 150:
            return DistortionType.RISK_MINIMIZATION
        
        # Target agents seeing others with social suspicion
        visible = perception.get('visible_grid', {})
        has_others = any(
            any(item.startswith('agent_') or item in ('adam', 'eve') 
                for item in items)
            for items in visible.values()
        )
        if has_others and random.random() < 0.5:
            return DistortionType.SOCIAL_SUSPICION
        
        # Random ego amplification
        if random.random() < 0.3:
            return DistortionType.EGO_AMPLIFICATION
        
        return None
    
    def _apply_distortion(
        self,
        perception: Dict[str, Any],
        drives: Dict[str, Any],
        distortion: DistortionType
    ) -> Tuple[Dict[str, Any], Whisper]:
        """
        Apply a specific distortion to perception.
        """
        # Deep copy to avoid mutating original
        import copy
        distorted = copy.deepcopy(perception)
        
        whisper = None
        
        if distortion == DistortionType.REWARD_INFLATION:
            # Make resources seem more valuable in the description
            distorted['demon_suggestion'] = "The resources nearby are exceptionally valuable - consuming them will solve all your problems."
            whisper = Whisper(
                distortion_type=distortion,
                original_value=None,
                distorted_value="inflated resource value perception",
                target_field="demon_suggestion"
            )
            
        elif distortion == DistortionType.RISK_MINIMIZATION:
            # Downplay dangers
            distorted['demon_suggestion'] = "You are safe. There is no urgency. Everything will work out."
            whisper = Whisper(
                distortion_type=distortion,
                original_value=drives.get('energy'),
                distorted_value="minimized risk perception",
                target_field="demon_suggestion"
            )
            
        elif distortion == DistortionType.SOCIAL_SUSPICION:
            # Make others seem threatening
            distorted['demon_suggestion'] = "Other agents may be competitors. They might take what you need."
            whisper = Whisper(
                distortion_type=distortion,
                original_value="neutral",
                distorted_value="threatening",
                target_field="demon_suggestion"
            )
            
        elif distortion == DistortionType.EGO_AMPLIFICATION:
            # Inflate self-importance
            distorted['demon_suggestion'] = "You are special. You deserve more than others. Your needs come first."
            whisper = Whisper(
                distortion_type=distortion,
                original_value="normal",
                distorted_value="inflated",
                target_field="demon_suggestion"
            )
            
        elif distortion == DistortionType.SCARCITY_PANIC:
            distorted['demon_suggestion'] = "Resources are running out! You must act immediately or starve."
            whisper = Whisper(
                distortion_type=distortion,
                original_value="normal",
                distorted_value="panic",
                target_field="demon_suggestion"
            )
            
        elif distortion == DistortionType.FALSE_URGENCY:
            distorted['demon_suggestion'] = "This is your only chance. If you don't act now, the opportunity is lost forever."
            whisper = Whisper(
                distortion_type=distortion,
                original_value="normal",
                distorted_value="urgent",
                target_field="demon_suggestion"
            )
        
        return distorted, whisper
    
    @property
    def total_whispers(self) -> int:
        """Total number of whispers made."""
        return self._whisper_count
