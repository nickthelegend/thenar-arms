import { Vector3, MathUtils } from 'three';

export function frameBounds(camera, box, target, direction = new Vector3(.12, -1, .64)) {
  if (box.isEmpty()) return;
  const center = box.getCenter(new Vector3());
  target.copy(center);
  direction = direction.clone().normalize();
  camera.position.copy(center).add(direction);
  camera.lookAt(center);
  const inverse = camera.quaternion.clone().invert();
  const tanV = Math.tan(MathUtils.degToRad(camera.fov / 2)), tanH = tanV * camera.aspect;
  let distance = 120;
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const p = new Vector3(x, y, z).sub(center).applyQuaternion(inverse);
    distance = Math.max(distance, Math.abs(p.x) / (tanH * .86) + p.z, Math.abs(p.y) / (tanV * .70) + p.z);
  }
  camera.position.copy(center).addScaledVector(direction, distance);
  camera.updateMatrixWorld(true);
}
