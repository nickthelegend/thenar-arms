import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { applyJointAngles, clampJointAngles } from '../src/kinematics.js';
import { frameBounds } from '../src/view-layout.js';

const root=path.resolve(import.meta.dirname,'..');
const dir=path.join(root,'public/models/so101');
const loader=new STLLoader();
for(const name of ['manifest.json','study-manifest.json']) {
 const m=JSON.parse(fs.readFileSync(path.join(dir,name)));const map={},scene=new THREE.Scene();
 for(const n of m.nodes){const g=new THREE.Group();g.position.fromArray(n.position);g.rotation.set(...n.rotation.map(THREE.MathUtils.degToRad));map[n.id]=g;(n.parent?map[n.parent]:scene).add(g)}
 const meshes=[];const parts=new Map(m.parts.map(p=>[p.id,p]));const geometries=new Map();
 for(const i of m.instances){
  if(!geometries.has(i.part)){const b=fs.readFileSync(path.join(dir,parts.get(i.part).file));geometries.set(i.part,loader.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)))}
  const mesh=new THREE.Mesh(geometries.get(i.part));mesh.position.fromArray(i.position);mesh.rotation.set(...i.rotation.map(THREE.MathUtils.degToRad));mesh.userData=i;map[i.node].add(mesh);meshes.push(mesh);
 }
 assert.equal(map.leader.position.x-map.follower.position.x,800);
 assert.equal(m.nodes.filter(n=>n.joint!==null).length,12);
 if(name.startsWith('study'))for(const [lo,hi]of m.limits)assert(hi-lo<=170);
 assert.throws(()=>clampJointAngles([NaN,0,0,0,0,0],m.limits));assert.throws(()=>clampJointAngles([0],m.limits));
 assert.deepEqual(clampJointAngles(Array(6).fill(10000),m.limits),m.limits.map(x=>x[1]));
 for(let j=0;j<6;j++){
  applyJointAngles(m.nodes,map,m.home,m.limits);scene.updateMatrixWorld(true);
  const before=meshes.map(x=>x.matrixWorld.clone());const q=[...m.home];q[j]+=10;
  applyJointAngles(m.nodes,map,q,m.limits);scene.updateMatrixWorld(true);
  for(const robot of ['leader','follower'])assert(meshes.some((x,i)=>x.userData.robot===robot&&!x.matrixWorld.equals(before[i])),`${robot} joint ${j} must move attached geometry`);
  for(const mesh of meshes)assert(mesh.matrixWorld.elements.every(Number.isFinite));
 }
 // Keep body/hardware rigidly attached within each link at all test poses.
 for(const robot of ['leader','follower'])for(let j=0;j<6;j++){
  const n=m.nodes.find(n=>n.id.startsWith(robot+'_')&&n.joint===j);assert(n);assert(Math.abs(n.rotation[0])<1e-10);assert(Math.abs(n.rotation[1])<1e-10);
 }
 applyJointAngles(m.nodes,map,m.home,m.limits);scene.updateMatrixWorld(true);
 const a=new THREE.Box3().setFromObject(map.follower),b=new THREE.Box3().setFromObject(map.leader);
 assert(!a.intersectsBox(b),'Separated display assemblies must not overlap at home');
 const box=a.clone().union(b);
 for(const aspect of [.5,1,1.5,2])for(const dir of [undefined,new THREE.Vector3(0,-1,.04),new THREE.Vector3(0,-.001,1)]){
  const camera=new THREE.PerspectiveCamera(35,aspect,.5,8000);camera.up.set(0,0,1);
  frameBounds(camera,box,new THREE.Vector3(),dir);
  for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
   const ndc=new THREE.Vector3(x,y,z).project(camera);
   assert(Math.abs(ndc.x)<=.861&&Math.abs(ndc.y)<=.701&&Math.abs(ndc.z)<1,'Both assemblies must fit with margins at narrow and wide aspect ratios');
  }
 }
 console.log('PASS',name,': 800 mm spacing; all 12 joints move; finite matrices; clamping; home display boxes separate.');
 console.log('PASS camera: all 8 bounding corners framed at 4 aspect ratios in isometric/front/top views.');
}
