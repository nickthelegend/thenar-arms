import { MathUtils } from 'three';

export function clampJointAngles(values, limits) {
  if (!Array.isArray(values) || values.length !== limits.length || values.some(x => !Number.isFinite(x))) {
    throw new Error('Six finite joint angles required');
  }
  return values.map((x, i) => MathUtils.clamp(x, ...limits[i]));
}

export function applyJointAngles(nodes, nodeMap, values, limits) {
  const angles = clampJointAngles(values, limits);
  for (const node of nodes) {
    if (node.joint !== null) {
      nodeMap[node.id].rotation.z = MathUtils.degToRad(angles[node.joint] * (node.factor ?? 1) + (node.offset ?? 0));
    }
  }
  return angles;
}
