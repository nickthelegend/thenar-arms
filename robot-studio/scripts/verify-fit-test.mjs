import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { addFitTestPlates } from '../src/fit-test.js';
const base=path.resolve(import.meta.dirname,'../public/models/so101');
const manifest=JSON.parse(fs.readFileSync(path.join(base,'study-manifest.json')));
const report=JSON.parse(fs.readFileSync(path.join(base,'fit-test/verification.json')));
const before=JSON.stringify({nodes:manifest.nodes,instances:manifest.instances});
addFitTestPlates(manifest,report);
assert.equal(before,JSON.stringify({nodes:manifest.nodes,instances:manifest.instances}),'Bench prints must not silently change the assembly under the existing motion report');
assert.equal(manifest.plates.length,4);
assert.equal(manifest.parts.filter(p=>p.kind==='test').length,3);
assert.deepEqual(manifest.plates.slice(0,2).map(p=>p.count),[2,3]);
for(const plate of manifest.plates.filter(p=>p.fitTest)){
 assert(plate.slicer.gcode_present);assert(fs.existsSync(path.join(base,plate.file)));
 for(const e of plate.entries){assert.equal(e.matrix.length,16);assert(e.matrix.every(Number.isFinite));}
}
for(const p of manifest.parts.filter(p=>p.kind==='test'))assert(fs.existsSync(path.join(base,p.file)));
assert.throws(()=>addFitTestPlates({},{}));
console.log('PASS: test meshes and plate downloads exist; no change to assembly/collision manifest.');
