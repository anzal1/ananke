/**
 * Timeline Panel - Scrubber, play/pause, speed controls
 */

import { useEffect, useRef } from 'react';
import { useEventStore } from '../state/eventStore';
import './Timeline.css';

export function Timeline() {
  const { currentTick, maxTick, isPlaying, playbackSpeed, setTick, play, pause, setSpeed, stepForward, stepBackward } =
    useEventStore();
  
  const intervalRef = useRef<number | null>(null);

  // Playback loop
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = window.setInterval(() => {
        stepForward();
      }, 1000 / playbackSpeed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, stepForward]);

  const progress = maxTick > 0 ? (currentTick / maxTick) * 100 : 0;

  return (
    <div className="timeline-panel">
      <div className="timeline-header">
        <h3>Timeline</h3>
        <span className="tick-display">
          {currentTick} / {maxTick}
        </span>
      </div>

      {/* Scrubber */}
      <div className="scrubber-container">
        <input
          type="range"
          min={0}
          max={maxTick}
          value={currentTick}
          onChange={(e) => setTick(parseInt(e.target.value))}
          className="scrubber"
        />
        <div className="scrubber-progress" style={{ width: `${progress}%` }} />
      </div>

      {/* Controls */}
      <div className="timeline-controls">
        <button onClick={stepBackward} title="Step Back">
          ⏮
        </button>
        <button onClick={isPlaying ? pause : play} className="play-button">
          {isPlaying ? '⏸' : '▶'}
        </button>
        <button onClick={stepForward} title="Step Forward">
          ⏭
        </button>
      </div>

      {/* Speed controls */}
      <div className="speed-controls">
        {[0.25, 1, 10, 100].map((speed) => (
          <button
            key={speed}
            onClick={() => setSpeed(speed)}
            className={playbackSpeed === speed ? 'active' : ''}
          >
            {speed}x
          </button>
        ))}
      </div>
    </div>
  );
}
