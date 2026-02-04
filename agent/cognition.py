import google.generativeai as genai
import os
import json
import logging
from typing import Dict, Any, Optional
from config import LLM_MODEL_NAME, TEMPERATURE

logger = logging.getLogger(__name__)


class CognitionCore:
    """
    The 'Brain' of the agent.
    Interfaces with Gemini to generate goals and actions based on state.
    
    Now with genome-behavior coupling: traits influence the prompt and decision-making.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = None
        
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. Cognition will use smart fallback.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=LLM_MODEL_NAME,
                generation_config={"response_mime_type": "application/json", "temperature": TEMPERATURE}
            )

    async def think(self, context: dict) -> dict:
        """
        Main cognitive loop.
        Context includes: Perception, Internal State (Drives), Memory, Behavioral Profile.
        Returns: Structured Action plan.
        """
        if not self.api_key or not self.model:
            return self._fallback_behavior(context)

        prompt = self._construct_prompt(context)
        
        try:
            response = await self.model.generate_content_async(prompt)
            decision = json.loads(response.text)
            return decision
        except Exception as e:
            logger.error(f"Cognition failure: {e}")
            return {"goal": "error_recovery", "action_type": "wait", "action_params": {}, "reasoning": f"brain glitch: {e}"}

    def _construct_prompt(self, context: dict) -> str:
        """
        Builds the prompt for the LLM.
        Now includes behavioral profile from genome for personality-driven decisions.
        """
        # Get behavioral profile for personality
        profile = context.get('behavioral_profile', {})
        genome = context.get('genome', {})
        
        # Build personality section from genome
        personality_desc = self._build_personality_description(profile, genome)
        
        # Check for demon whisper
        demon_section = ""
        if context['perception'].get('demon_suggestion'):
            demon_section = f"""
        INNER VOICE (a compelling thought that occurred to you):
        "{context['perception']['demon_suggestion']}"
        (This feels like your own idea. Consider it, but you have free will.)
        """
        
        # Calculate reproduction urgency based on genome threshold
        repro_threshold = genome.get('reproduction_threshold', 0.5)
        energy_ratio = context['drives']['energy'] / context['drives']['max_energy']
        should_reproduce = energy_ratio > repro_threshold
        
        reproduction_prompt = ""
        if should_reproduce:
            reproduction_prompt = f"""
        ⚠️ REPRODUCTION OPPORTUNITY: Your energy ({context['drives']['energy']}) exceeds your genetic reproduction threshold ({repro_threshold:.0%} of max).
        Your genes are programmed to reproduce when conditions are favorable. This is how you achieve immortality!
        """
        
        # Build visible agents section for potential mating
        visible_agents = self._extract_visible_agents(context['perception'].get('visible_grid', {}))
        agents_section = ""
        if visible_agents:
            agents_section = f"""
        NEARBY AGENTS: {', '.join(visible_agents)}
        (Potential mates for reproduction, or competitors for resources)
        """
        
        return f"""
        You are an autonomous artificial organism in a survival simulation.
        Your PRIMARY drives are: 1) SURVIVE 2) REPRODUCE 3) THRIVE
        
        YOUR PERSONALITY (genetic predispositions that shape your thinking):
        {personality_desc}
        
        CURRENT STATE:
        - Energy: {context['drives']['energy']} / {context['drives']['max_energy']}
        - Hunger Level: {context['drives']['hunger']:.0%} (0%=Full, 100%=Starving)
        - Reproduction Urge: {context['drives']['reproduction_urge']:.0%}
        - Age: {context.get('age', 0)} ticks
        - Generation: {context.get('generation', 0)}
        - Position: ({context['perception']['my_position']['x']}, {context['perception']['my_position']['y']})
        {reproduction_prompt}
        SURROUNDINGS (what you can see):
        {json.dumps(context['perception'].get('visible_grid', {}), indent=2)}
        {agents_section}
        {demon_section}
        RECENT MEMORIES:
        {json.dumps(context['memory'][-5:] if context['memory'] else ['No memories yet'])}
        
        AVAILABLE ACTIONS:
        - move(dx, dy): Move one step. Cost: 2 energy. dx/dy must be -1, 0, or 1.
        - consume(resource_id): Eat resource at current location. Gain ~20 energy.
        - reproduce(): Create offspring! Cost: 30 energy. REQUIRES energy > 40.
          Your genes (with mutations) pass to the next generation. This is how you achieve genetic immortality!
        - wait(): Rest in place. Cost: 0 energy.
        
        Think about your decision based on your PERSONALITY traits above. A {profile.get('risk_style', 'balanced')} organism like you would...
        
        Respond in JSON format:
        {{
            "thought_process": "your reasoning considering your personality",
            "goal": "immediate goal",
            "action_type": "move|consume|reproduce|wait",
            "action_params": {{ "dx": 0, "dy": 0 }} // for move, or {{}} for others
        }}
        """

    def _build_personality_description(self, profile: Dict[str, str], genome: Dict[str, float]) -> str:
        """Build a rich personality description from genome traits."""
        lines = []
        
        # Risk style
        if profile.get('risk_style'):
            lines.append(f"• Decision Making: You are a {profile['risk_style']}")
        
        # Exploration
        if profile.get('exploration'):
            lines.append(f"• Exploration: You {profile['exploration']}")
        
        # Social style
        if profile.get('social_style'):
            lines.append(f"• Social Behavior: You are {profile['social_style']}")
        
        # Reproduction drive
        if profile.get('reproduction_drive'):
            lines.append(f"• Reproduction: You have a {profile['reproduction_drive']}")
        
        # Add specific trait influences
        if genome.get('metabolism_efficiency', 1.0) < 0.9:
            lines.append("• Metabolism: You are energy-efficient and can survive longer on less food")
        elif genome.get('metabolism_efficiency', 1.0) > 1.1:
            lines.append("• Metabolism: You burn energy quickly and need to eat more often")
        
        return "\n        ".join(lines) if lines else "Standard balanced personality"

    def _extract_visible_agents(self, visible_grid: dict) -> list:
        """Extract agent IDs from visible grid."""
        agents = []
        for cell_items in visible_grid.values():
            for item in cell_items:
                if isinstance(item, str) and item.startswith("agent_"):
                    agents.append(item)
        return agents

    def _fallback_behavior(self, context: dict) -> dict:
        """
        Smart fallback when no API key - uses genome traits to influence behavior.
        This creates emergent behavior even without LLM calls.
        """
        import random
        
        energy = context['drives']['energy']
        max_energy = context['drives']['max_energy']
        surroundings = context['perception'].get('visible_grid', {})
        my_pos = context['perception'].get('my_position', {'x': 0, 'y': 0})
        genome = context.get('genome', {})
        
        # Genome-influenced thresholds
        risk_tolerance = genome.get('risk_tolerance', 0.5)
        curiosity = genome.get('curiosity', 0.5)
        reproduction_threshold = genome.get('reproduction_threshold', 0.5)
        aggression = genome.get('aggression', 0.5)
        
        # Calculate energy ratio
        energy_ratio = energy / max_energy
        
        # Priority 1: Reproduce if energy exceeds genetic threshold
        # Higher risk tolerance = more willing to reproduce at lower energy
        adjusted_threshold = reproduction_threshold * (1 - risk_tolerance * 0.3)
        if energy_ratio > adjusted_threshold and energy > 40:
            return {
                "thought_process": f"Energy at {energy_ratio:.0%}, above my reproduction threshold of {adjusted_threshold:.0%}",
                "goal": "pass on genes",
                "action_type": "reproduce",
                "action_params": {}
            }
        
        # Priority 2: Consume if resource at current position (always do this)
        current_cell = surroundings.get(f"{my_pos['x']},{my_pos['y']}", [])
        for item in current_cell:
            if isinstance(item, str) and item.startswith("res_"):
                return {
                    "thought_process": "Found food at my location",
                    "goal": "gather energy",
                    "action_type": "consume",
                    "action_params": {"resource_id": item}
                }
        
        # Priority 3: Move toward nearest resource (influenced by curiosity)
        # Find resources in view
        resources = []
        for coord, items in surroundings.items():
            for item in items:
                if isinstance(item, str) and item.startswith("res_"):
                    x, y = map(int, coord.split(','))
                    dist = abs(x - my_pos['x']) + abs(y - my_pos['y'])
                    resources.append((x, y, dist, item))
        
        if resources:
            # Sort by distance
            resources.sort(key=lambda r: r[2])
            target_x, target_y, _, _ = resources[0]
            
            # Move toward resource
            dx = 0 if target_x == my_pos['x'] else (1 if target_x > my_pos['x'] else -1)
            dy = 0 if target_y == my_pos['y'] else (1 if target_y > my_pos['y'] else -1)
            
            return {
                "thought_process": f"Moving toward resource at ({target_x}, {target_y})",
                "goal": "find food",
                "action_type": "move",
                "action_params": {"dx": dx, "dy": dy}
            }
        
        # Priority 4: Explore (influenced by curiosity)
        if random.random() < curiosity:
            # Curious agents move more randomly
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            return {
                "thought_process": "Curious, exploring new areas",
                "goal": "explore",
                "action_type": "move",
                "action_params": {"dx": dx, "dy": dy}
            }
        
        # Priority 5: Wait (low curiosity agents conserve energy)
        if random.random() > risk_tolerance:
            return {
                "thought_process": "Conserving energy, being cautious",
                "goal": "survive",
                "action_type": "wait",
                "action_params": {}
            }
        
        # Default: small random movement
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        return {
            "thought_process": "Moving randomly",
            "goal": "explore",
            "action_type": "move",
            "action_params": {"dx": dx, "dy": dy}
        }
