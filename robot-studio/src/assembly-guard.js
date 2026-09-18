import { MeshBVH } from 'three-mesh-bvh';
import { Box3,Matrix4,Vector3,Ray,DoubleSide } from 'three';

// A preview guard for discrete requested poses. Does not certify the path
// between poses, load capacity, flexible wires or physical tolerances.
export function createAssemblyGuard(meshes){
 const bodies=meshes.filter(m=>['follower','leader'].includes(m.userData.robot));
 // These six purchased horn/shaft pairs intentionally share a mating surface.
 // Skip only the matching interface, not other motor/horn collisions.
 const motors=bodies.filter(m=>m.userData.part==='MG996R_body_R3');
 function intendedInterface(a,b){
  if(a.userData.part==='metal_horn_R3')[a,b]=[b,a];
  return a.userData.part==='MG996R_body_R3'&&b.userData.part==='metal_horn_R3'&&motors[Number(b.userData.id.match(/_(\d+)$/)?.[1])]===a;
 }
 for(const m of bodies){const g=m.geometry;g.computeBoundingBox();if(!g.boundsTree)g.boundsTree=new MeshBVH(g,{maxLeafSize:10});}
 const direction=new Vector3(.371,.529,.763).normalize();
 function contains(a,b,t){
  const p=new Vector3().fromBufferAttribute(b.geometry.attributes.position,0).applyMatrix4(t);
  if(!a.geometry.boundingBox.containsPoint(p))return false;
  const hits=a.geometry.boundsTree.raycast(new Ray(p,direction),DoubleSide).map(x=>x.distance).filter(x=>x>1e-5).sort((x,y)=>x-y);
  return hits.filter((v,i)=>!i||v-hits[i-1]>1e-4).length%2===1;
 }
 return ()=>{
  const boxes=bodies.map(m=>m.geometry.boundingBox.clone().applyMatrix4(m.matrixWorld));
  for(let i=0;i<bodies.length;i++){
   const a=bodies[i];
   if(boxes[i].min.z<-.2){
    const attr=a.geometry.attributes.position,e=a.matrixWorld.elements;
    for(let k=0;k<attr.count;k++)if(e[2]*attr.getX(k)+e[6]*attr.getY(k)+e[10]*attr.getZ(k)+e[14]<-.2)return {type:'table',a:a.userData.part};
   }
   for(let j=i+1;j<bodies.length;j++){
    const b=bodies[j];
    if(a.userData.robot!==b.userData.robot||a.userData.node===b.userData.node||intendedInterface(a,b)||!boxes[i].intersectsBox(boxes[j]))continue;
    const t=new Matrix4().copy(a.matrixWorld).invert().multiply(b.matrixWorld);
    if(a.geometry.boundsTree.intersectsGeometry(b.geometry,t)||contains(a,b,t)||contains(b,a,t.clone().invert()))return {type:'collision',a:a.userData.part,b:b.userData.part};
   }
  }
  return null;
 };
}
