/**
 * EventStream Panel - Scrolling event log
 */

import { useEffect, useRef } from 'react';
import { useEventStore, type SimulationEvent } from '../state/eventStore';
import './EventStream.css';

function formatEvent(event: SimulationEvent): string {
  const seq = event.sequence.toString().padStart(4, '0');
  
  switch (event.type) {
    case 'ledger_initialized':
      return `[${seq}] 📜 Ledger initialized`;
    
    case 'agent_birth': {
      const d = event.details as { agent_id: string; agent_type: string };
      const icon = d.agent_type === 'origin' ? '👤' : '👶';
      return `[${seq}] ${icon} ${d.agent_id} born (${d.agent_type})`;
    }
    
    case 'agent_action': {
      const d = event.details as { agent_id: string; action: string; outcome: string };
      return `[${seq}] ⚡ ${d.agent_id} ${d.action}: ${d.outcome}`;
    }
    
    case 'agent_death': {
      const d = event.details as { agent_id: string; cause: string };
      return `[${seq}] 💀 ${d.agent_id} died: ${d.cause}`;
    }
    
    case 'resource_spawn': {
      const d = event.details as { id: string; x: number; y: number };
      return `[${seq}] 🌱 ${d.id} spawned at (${d.x}, ${d.y})`;
    }
    
    case 'resource_deplete': {
      const d = event.details as { id: string };
      return `[${seq}] 🍽️ ${d.id} consumed`;
    }
    
    case 'demon_whisper': {
      const d = event.details as { agent_id: string; distortion_type: string };
      return `[${seq}] 👁️ ${d.agent_id} received whisper: ${d.distortion_type}`;
    }
    
    default:
      return `[${seq}] ${event.type}`;
  }
}

function getEventClass(event: SimulationEvent): string {
  switch (event.type) {
    case 'agent_birth': return 'event-birth';
    case 'agent_death': return 'event-death';
    case 'agent_action': return 'event-action';
    case 'resource_spawn': return 'event-spawn';
    case 'resource_deplete': return 'event-consume';
    case 'demon_whisper': return 'event-whisper';
    default: return '';
  }
}

export function EventStream() {
  const events = useEventStore((state) => state.events);
  const currentTick = useEventStore((state) => state.currentTick);
  const setTick = useEventStore((state) => state.setTick);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Filter events up to current tick
  const visibleEvents = events.filter((e) => e.sequence <= currentTick).slice(-100);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [visibleEvents.length]);

  return (
    <div className="event-stream-panel">
      <div className="event-stream-header">
        <h3>Event Stream</h3>
        <span className="event-count">{visibleEvents.length} events</span>
      </div>
      <div className="event-stream-list" ref={scrollRef}>
        {visibleEvents.map((event) => (
          <div
            key={event.sequence}
            className={`event-item ${getEventClass(event)}`}
            onClick={() => setTick(event.sequence)}
          >
            {formatEvent(event)}
          </div>
        ))}
      </div>
    </div>
  );
}
