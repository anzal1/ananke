/**
 * World Canvas - Main 3D scene with orthographic camera
 * True top-down 2D view (XY plane)
 */

import { Canvas } from '@react-three/fiber';
import { OrthographicCamera } from '@react-three/drei';
import { AgentMesh } from './AgentMesh';
import { ResourceMesh } from './ResourceMesh';
import { useEventStore } from '../state/eventStore';

const WORLD_SIZE = 100;

function Scene() {
  const agents = useEventStore((state) => state.agents);
  const resources = useEventStore((state) => state.resources);

  return (
    <>
      {/* Orthographic camera - true top-down 2D view on XY plane */}
      <OrthographicCamera
        makeDefault
        position={[WORLD_SIZE / 2, WORLD_SIZE / 2, 100]}
        zoom={6}
        near={0.1}
        far={1000}
      />

      {/* Lighting for 2D view */}
      <ambientLight intensity={1} />

      {/* World grid - XY plane */}
      <gridHelper 
        args={[WORLD_SIZE, 20, '#1a1a2e', '#16213e']} 
        rotation={[Math.PI / 2, 0, 0]}
        position={[WORLD_SIZE / 2, WORLD_SIZE / 2, -1]}
      />

      {/* Resources - on XY plane */}
      {Array.from(resources.values()).map((resource) => (
        <ResourceMesh key={resource.id} resource={resource} />
      ))}

      {/* Agents - on XY plane */}
      {Array.from(agents.values())
        .filter((a) => a.isAlive)
        .map((agent) => (
          <AgentMesh key={agent.id} agent={agent} />
        ))}
    </>
  );
}

export function World() {
  return (
    <div style={{ width: '100%', height: '100%', background: '#0a0a0f' }}>
      <Canvas>
        <Scene />
      </Canvas>
    </div>
  );
}
