/**
 * Ananke Observatory - Main App
 */

import { useEffect, useRef } from 'react';
import { World } from './canvas/World';
import { Timeline } from './panels/Timeline';
import { Inspector } from './panels/Inspector';
import { EventStream } from './panels/EventStream';
import { useEventStore, loadEventsFromFile } from './state/eventStore';
import './App.css';

function App() {
  const loadEvents = useEventStore((state) => state.loadEvents);
  const maxTick = useEventStore((state) => state.maxTick);
  const setTick = useEventStore((state) => state.setTick);
  const pollRef = useRef<number | null>(null);
  const lastEventCount = useRef(0);

  useEffect(() => {
    // Initial load
    loadEventsFromFile('/divine_ledger.jsonl')
      .then((events) => {
        loadEvents(events);
        lastEventCount.current = events.length;
        console.log(`Loaded ${events.length} events`);
      })
      .catch((err) => {
        console.error('Failed to load events:', err);
        loadSampleEvents(loadEvents);
      });

    // Poll for new events every 500ms (live mode)
    pollRef.current = window.setInterval(async () => {
      try {
        const events = await loadEventsFromFile('/divine_ledger.jsonl');
        if (events.length > lastEventCount.current) {
          console.log(`New events: ${events.length - lastEventCount.current}`);
          lastEventCount.current = events.length;
          loadEvents(events);
          // Auto-scroll to latest
          setTick(events[events.length - 1].sequence);
        }
      } catch {
        // Ignore errors during polling
      }
    }, 500);

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
      }
    };
  }, [loadEvents, setTick]);

  return (
    <div className="observatory">
      <header className="observatory-header">
        <h1>Ananke Observatory</h1>
        <span className="subtitle">Theological Ontology Simulation</span>
        <span className="live-badge">● LIVE</span>
        {maxTick > 0 && <span className="event-badge">{maxTick} events</span>}
      </header>

      <div className="observatory-main">
        <Timeline />
        <div className="canvas-container">
          <World />
        </div>
        <Inspector />
      </div>

      <EventStream />
    </div>
  );
}

// Sample events for development
function loadSampleEvents(loadEvents: (events: unknown[]) => void) {
  const sampleEvents = [
    { sequence: 0, timestamp: Date.now(), type: 'ledger_initialized', details: {} },
    {
      sequence: 1,
      timestamp: Date.now(),
      type: 'agent_birth',
      details: {
        agent_id: 'adam',
        agent_type: 'origin',
        position: { x: 45, y: 50 },
        genome: { risk_tolerance: 0.5, curiosity: 0.7, social_bias: 0.6, memory_retention: 1.0 },
      },
    },
    {
      sequence: 2,
      timestamp: Date.now(),
      type: 'agent_birth',
      details: {
        agent_id: 'eve',
        agent_type: 'origin',
        position: { x: 55, y: 50 },
        genome: { risk_tolerance: 0.4, curiosity: 0.8, social_bias: 0.7, memory_retention: 1.0 },
      },
    },
  ];

  loadEvents(sampleEvents);
}

export default App;
