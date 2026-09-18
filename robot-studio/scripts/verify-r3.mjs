import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { applyJointAngles } from '../src/kinematics.js';
import { followerBelowTable } from '../src/r3-ui.js';
const root=new URL('../public/models/so101/',import.meta.url);
const m=JSON.parse(fs.readFileSync(new URL('study-manifest.json',root)));
const sha=b=>createHash('sha256').update(b).digest('hex');
const motion=JSON.parse(fs.readFileSync(new URL('motion-verification.json',root)));
assert.equal(motion.manifest_sha256,sha(fs.readFileSync(new URL('study-manifest.json',root))),'Stale motion report');
assert(m.revision.startsWith('SO101-MG996R-R3'));
const parts=new Map(m.parts.map(p=>[p.id,p])),nodes={},meshes=[],scene=new THREE.Scene();
for(const n of m.nodes){const g=new THREE.Group();g.position.fromArray(n.position);g.rotation.set(...n.rotation.map(THREE.MathUtils.degToRad));g.userData=n;nodes[n.id]=g;(n.parent?nodes[n.parent]:scene).add(g)}
const loader=new STLLoader(),geometries=new Map();
for(const p of m.parts){const b=fs.readFileSync(new URL(p.file,root));geometries.set(p.id,loader.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)))}
for(const i of m.instances){const mesh=new THREE.Mesh(geometries.get(i.part));mesh.position.fromArray(i.position);mesh.rotation.set(...i.rotation.map(THREE.MathUtils.degToRad));mesh.userData=i;nodes[i.node].add(mesh);meshes.push(mesh)}
const follower=meshes.filter(x=>x.userData.robot==='follower');
assert.equal(follower.filter(x=>parts.get(x.userData.part).kind==='print').length,7);
assert.equal(follower.filter(x=>x.userData.part==='MG996R_body_R3').length,6);
assert.equal(follower.filter(x=>x.userData.part==='metal_horn_R3').length,6);
const followerPlates=m.plates.filter(p=>p.robot!=='leader');
assert.equal(followerPlates.length,2);
assert.equal(followerPlates.flatMap(p=>p.entries).length,7);
for(const p of followerPlates){assert(p.prototype);assert(p.file.includes('MG996R_R3'));assert(fs.existsSync(new URL(p.file,root)));for(const e of p.entries)assert(parts.has(e.part))}
function pose(q){applyJointAngles(m.nodes,nodes,q,m.limits);scene.updateMatrixWorld(true)}
pose(m.home);assert(!followerBelowTable(meshes),'Home enters table');
const home=follower.map(x=>x.matrixWorld.clone());
for(let j=0;j<6;j++){const q=[...m.home];q[j]+=5;pose(q);assert(follower.some((x,i)=>x.matrixWorld.elements.some((v,k)=>Math.abs(v-home[i].elements[k])>1e-5)),`Joint ${j} did not move`);assert(follower.every(x=>x.matrixWorld.elements.every(Number.isFinite)))}
pose([0,80,0,0,0,0]);assert(followerBelowTable(meshes),'Known table collision was not detected');
pose(m.home);
assert.equal(m.prototype_reports.interfaces.all_checks_passed,true);
assert(m.prototype_reports.build.print_units.every(p=>p.watertight&&p.shells===1));
for(const p of m.prototype_reports.build.print_units)assert.equal(p.sha256,sha(fs.readFileSync(new URL('follower-r3/print-parts/'+p.file,root))),p.file);
const plateReport=m.prototype_reports.plates;
const problems=!plateReport.toolpath_screen?.all_coarse_screens_passed||plateReport.plates.some(p=>p.slicer.diagnostics?.length);
if(problems)assert.equal(plateReport.sliced_downloads_released,false,'Unreviewed toolpaths must not be released');
console.log('R3: 7 units, 6 servos + 6 moving horns, 2 genuine converted plates, all joints move, tabletop guard detects known collision.');
console.log('R3: source mesh hashes and motion-manifest hash match; toolpath review gates sliced downloads.');
