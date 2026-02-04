/**
 * ResourceMesh - Renders resources as small dots on XY plane
 */

import type { Resource } from '../state/eventStore';

interface ResourceMeshProps {
  resource: Resource;
}

export function ResourceMesh({ resource }: ResourceMeshProps) {
  const size = 0.4 + (resource.value / 20) * 0.3;

  // Position on XY plane (Z is depth)
  return (
    <mesh position={[resource.x, resource.y, 0]}>
      <circleGeometry args={[size, 16]} />
      <meshBasicMaterial color="#4ade80" transparent opacity={0.8} />
    </mesh>
  );
}
