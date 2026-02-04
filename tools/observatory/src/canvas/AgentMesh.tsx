/**
 * AgentMesh - Renders agents as circles on XY plane
 * Color = dominant genome trait
 * Radius = energy level
 */

import type { Agent } from '../state/eventStore';

interface AgentMeshProps {
  agent: Agent;
}

// Map genome traits to colors
function getAgentColor(genome: Record<string, number>): string {
  const riskTolerance = genome.risk_tolerance ?? 0.5;
  const curiosity = genome.curiosity ?? 0.5;
  const socialBias = genome.social_bias ?? 0.5;

  // High risk = red, high curiosity = green, high social = blue
  const r = Math.floor(100 + riskTolerance * 155);
  const g = Math.floor(100 + curiosity * 155);
  const b = Math.floor(100 + socialBias * 155);

  return `rgb(${r}, ${g}, ${b})`;
}

// Scale radius based on energy
function getRadius(energy: number): number {
  const normalizedEnergy = Math.max(0.1, Math.min(energy / 100, 2));
  return 1 + normalizedEnergy * 0.5;
}

export function AgentMesh({ agent }: AgentMeshProps) {
  const color = getAgentColor(agent.genome);
  const radius = getRadius(agent.energy);
  const isOrigin = agent.agentType === 'origin';

  // Position on XY plane (Z is depth)
  return (
    <group position={[agent.x, agent.y, 1]}>
      {/* Main agent circle */}
      <mesh>
        <circleGeometry args={[radius, 32]} />
        <meshBasicMaterial color={color} />
      </mesh>

      {/* Origin glow ring */}
      {isOrigin && (
        <mesh position={[0, 0, 0.1]}>
          <ringGeometry args={[radius + 0.3, radius + 0.6, 32]} />
          <meshBasicMaterial color="#ffd700" transparent opacity={0.7} />
        </mesh>
      )}
    </group>
  );
}
