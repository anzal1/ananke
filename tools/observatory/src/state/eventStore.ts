/**
 * Event Store - Zustand store for simulation events
 * Loads and manages the divine_ledger.jsonl event stream
 */

import { create } from 'zustand';

export interface SimulationEvent {
  sequence: number;
  timestamp: number;
  type: string;
  details: Record<string, unknown>;
}

export interface Agent {
  id: string;
  x: number;
  y: number;
  energy: number;
  agentType: 'origin' | 'descendant';
  genome: Record<string, number>;
  isAlive: boolean;
}

export interface Resource {
  id: string;
  x: number;
  y: number;
  value: number;
}

interface EventStore {
  events: SimulationEvent[];
  agents: Map<string, Agent>;
  resources: Map<string, Resource>;
  currentTick: number;
  maxTick: number;
  isPlaying: boolean;
  playbackSpeed: number;
  
  // Actions
  loadEvents: (events: SimulationEvent[]) => void;
  setTick: (tick: number) => void;
  stepForward: () => void;
  stepBackward: () => void;
  play: () => void;
  pause: () => void;
  setSpeed: (speed: number) => void;
  replayToTick: (tick: number) => void;
}

export const useEventStore = create<EventStore>((set, get) => ({
  events: [],
  agents: new Map(),
  resources: new Map(),
  currentTick: 0,
  maxTick: 0,
  isPlaying: false,
  playbackSpeed: 1,

  loadEvents: (events) => {
    // Find max tick by counting unique ticks or using sequence
    const maxTick = events.length > 0 ? events[events.length - 1].sequence : 0;
    
    set({ events, maxTick });
    
    // Replay to build initial state
    get().replayToTick(maxTick);
  },

  setTick: (tick) => {
    const { maxTick } = get();
    const clampedTick = Math.max(0, Math.min(tick, maxTick));
    get().replayToTick(clampedTick);
  },

  stepForward: () => {
    const { currentTick, maxTick } = get();
    if (currentTick < maxTick) {
      get().replayToTick(currentTick + 1);
    }
  },

  stepBackward: () => {
    const { currentTick } = get();
    if (currentTick > 0) {
      get().replayToTick(currentTick - 1);
    }
  },

  play: () => set({ isPlaying: true }),
  pause: () => set({ isPlaying: false }),
  setSpeed: (speed) => set({ playbackSpeed: speed }),

  replayToTick: (targetTick) => {
    const { events } = get();
    const agents = new Map<string, Agent>();
    const resources = new Map<string, Resource>();

    // Replay all events up to targetTick
    for (const event of events) {
      if (event.sequence > targetTick) break;

      switch (event.type) {
        case 'agent_birth': {
          const d = event.details as {
            agent_id: string;
            position: { x: number; y: number };
            agent_type: string;
            genome: Record<string, number>;
          };
          agents.set(d.agent_id, {
            id: d.agent_id,
            x: d.position.x,
            y: d.position.y,
            energy: 100,
            agentType: d.agent_type as 'origin' | 'descendant',
            genome: d.genome,
            isAlive: true,
          });
          break;
        }

        case 'agent_action': {
          const d = event.details as {
            agent_id: string;
            position: { x: number; y: number };
            energy_after: number;
          };
          const agent = agents.get(d.agent_id);
          if (agent) {
            agent.x = d.position.x;
            agent.y = d.position.y;
            agent.energy = d.energy_after;
          }
          break;
        }

        case 'agent_death': {
          const d = event.details as { agent_id: string };
          const agent = agents.get(d.agent_id);
          if (agent) {
            agent.isAlive = false;
          }
          break;
        }

        case 'resource_spawn': {
          const d = event.details as {
            id: string;
            x: number;
            y: number;
            value: number;
          };
          resources.set(d.id, {
            id: d.id,
            x: d.x,
            y: d.y,
            value: d.value,
          });
          break;
        }

        case 'resource_deplete': {
          const d = event.details as { id: string };
          resources.delete(d.id);
          break;
        }
      }
    }

    set({ agents, resources, currentTick: targetTick });
  },
}));


// Helper to load events from file
export async function loadEventsFromFile(filePath: string): Promise<SimulationEvent[]> {
  const response = await fetch(filePath);
  const text = await response.text();
  
  const events: SimulationEvent[] = [];
  for (const line of text.split('\n')) {
    if (line.trim()) {
      try {
        events.push(JSON.parse(line));
      } catch {
        console.warn('Failed to parse event:', line);
      }
    }
  }
  
  return events;
}
