import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import * as T from 'three';
import {STLLoader} from 'three/addons/loaders/STLLoader.js';
import {applyJointAngles} from '../src/kinematics.js';
import {createAssemblyGuard} from '../src/assembly-guard.js';
const root=new URL('../public/models/so101/',import.meta.url);
const m=JSON.parse(fs.readFileSync(new URL('study-manifest.json',root)));
const e=m.encoder_leader;assert(e);assert(e.verification.all_interfaces_passed);
assert.equal(e.plates.plates.length,3);assert.equal(e.plates.part_count,37);
const nodes={},scene=new T.Scene(),gs=new Map(),meshes=[],loader=new STLLoader();
for(const n of m.nodes){const g=new T.Group();g.position.fromArray(n.position);g.rotation.set(...n.rotation.map(T.MathUtils.degToRad));nodes[n.id]=g;(n.parent?nodes[n.parent]:scene).add(g)}
for(const p of m.parts){const b=fs.readFileSync(new URL(p.file,root));gs.set(p.id,loader.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)))}
for(const i of m.instances){const x=new T.Mesh(gs.get(i.part));x.position.fromArray(i.position);x.rotation.set(...i.rotation.map(T.MathUtils.degToRad));x.userData=i;nodes[i.node].add(x);meshes.push(x)}
for(const [file,hash]of Object.entries(e.verification.files))assert.equal(createHash('sha256').update(fs.readFileSync(new URL('encoder-leader-l1/'+file,root))).digest('hex'),hash);
const guard=createAssemblyGuard(meshes);function check(q){applyJointAngles(m.nodes,nodes,q,m.limits);scene.updateMatrixWorld(true);return guard()}
assert.equal(check(m.home),null,'Home must not be blocked');
for(let j=0;j<6;j++){const q=[...m.home];q[j]+=2;assert.equal(check(q),null,`Small motion joint ${j} blocked`)}
for(const p of e.verification.poses.filter(p=>p.overlaps.length))assert(check(p.angles_degrees),`Missed ${p.name}`);
assert(check([0,80,0,0,0,0]),'Missed table');
console.log('PASS encoder: 37 pieces / 3 plates; source hashes; 6 interfaces; home and six small moves clear; unsafe sample poses blocked.');
