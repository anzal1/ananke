/**
 * Inspector Panel - Agent profile, genome bars, cognitive trace
 */

import { useState } from 'react';
import { useEventStore, type Agent } from '../state/eventStore';
import './Inspector.css';

interface InspectorProps {
  selectedAgentId?: string | null;
  onSelectAgent?: (id: string | null) => void;
}

function GenomeBar({ label, value }: { label: string; value: number }) {
  const percentage = Math.min(100, Math.max(0, value * 100));
  
  return (
    <div className="genome-bar">
      <span className="genome-label">{label}</span>
      <div className="genome-track">
        <div className="genome-fill" style={{ width: `${percentage}%` }} />
      </div>
      <span className="genome-value">{value.toFixed(2)}</span>
    </div>
  );
}

function AgentProfile({ agent }: { agent: Agent }) {
  return (
    <div className="agent-profile">
      <div className="agent-header">
        <span className={`agent-badge ${agent.agentType}`}>
          {agent.agentType}
        </span>
        <h3>{agent.id}</h3>
      </div>

      <div className="agent-stats">
        <div className="stat">
          <span className="stat-label">Energy</span>
          <span className="stat-value">{agent.energy}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Position</span>
          <span className="stat-value">({agent.x}, {agent.y})</span>
        </div>
        <div className="stat">
          <span className="stat-label">Status</span>
          <span className={`stat-value ${agent.isAlive ? 'alive' : 'dead'}`}>
            {agent.isAlive ? 'Alive' : 'Dead'}
          </span>
        </div>
      </div>

      <div className="genome-section">
        <h4>Genome</h4>
        <GenomeBar label="Risk Tolerance" value={agent.genome.risk_tolerance ?? 0.5} />
        <GenomeBar label="Curiosity" value={agent.genome.curiosity ?? 0.5} />
        <GenomeBar label="Social Bias" value={agent.genome.social_bias ?? 0.5} />
        <GenomeBar label="Memory" value={agent.genome.memory_retention ?? 0.5} />
        <GenomeBar label="Metabolism" value={(agent.genome.metabolism_efficiency ?? 1) / 2} />
      </div>
    </div>
  );
}

export function Inspector({ selectedAgentId }: InspectorProps) {
  const agents = useEventStore((state) => state.agents);
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);

  const displayAgentId = selectedAgentId || hoveredAgent;
  const agent = displayAgentId ? agents.get(displayAgentId) : null;

  // List all agents
  const agentList = Array.from(agents.values()).filter(a => a.isAlive);

  return (
    <div className="inspector-panel">
      <div className="inspector-header">
        <h3>Inspector</h3>
      </div>

      {agent ? (
        <AgentProfile agent={agent} />
      ) : (
        <div className="no-selection">
          <p>Select an agent to inspect</p>
        </div>
      )}

      <div className="agent-list">
        <h4>Agents ({agentList.length})</h4>
        {agentList.map((a) => (
          <div
            key={a.id}
            className={`agent-list-item ${a.id === displayAgentId ? 'selected' : ''}`}
            onMouseEnter={() => setHoveredAgent(a.id)}
            onMouseLeave={() => setHoveredAgent(null)}
          >
            <span className={`dot ${a.agentType}`} />
            <span className="agent-name">{a.id}</span>
            <span className="agent-energy">{a.energy}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
