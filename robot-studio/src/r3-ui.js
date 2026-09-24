import {modelUrl} from './asset-path.js';
const ROOT=modelUrl('follower-r3/');
export const isR3=m=>m?.revision?.startsWith('SO101-MG996R-R3');
function toolpathNotice(manifest){
 const report=manifest.prototype_reports.plates;
 if(report.sliced_downloads_released)return 'Geometry-only layout: choose the correct printer, material and settings before printing.';
 const candidates=report.toolpath_screen?.plates.reduce((n,p)=>n+p.missing_component_candidates.length,0);
 return `Full-plate print not cleared. Slicer clipping diagnostics${candidates!=null?` and ${candidates} coarse toolpath-review candidates`:''} remain unresolved. Candidates are not confirmed defects. Downloads contain geometry only; sliced projects/G-code are withheld. Review sliced layers before any single-part fit print.`;
}
export function r3Notice(motion){
 if(motion?.leader){const e=motion.leader,c=motion.collisions;return `Internal-overlap samples: follower ${c.tested_poses-c.failed_sampled_poses}/${c.tested_poses} clear; leader ${e.tested_poses-e.failed_poses}/${e.tested_poses} clear. Table hits: follower ${c.table_intersection_poses}, leader ${e.table_intersection_poses}. Detected requested-pose collisions are blocked; paths and physical operation remain untested.`;}
 const c=motion?.collisions;
 return c?`${c.tested_poses-c.failed_sampled_poses}/${c.tested_poses} sampled poses clear of internal part overlaps. ${c.table_intersection_poses} hit the tabletop. Physical fit and load capacity remain untested.`:'Current collision report unavailable; do not infer clearance from the animation.';
}
export function renderR3Plates(manifest,index,onSelect){
 const p=manifest.plates[index];
 document.querySelector('#panel-heading').textContent='Bambu Lab P1S · MG996R R3';
 document.querySelector('#panel-body').innerHTML=`<p class="group-title">Actual MG996R follower parts</p><p class="panel-help">Seven original-derived printing units. Fixed bracket pairs are joined so they do not need STS servo-case mounting screws.</p><div class="plate-list">${manifest.plates.map((p,i)=>`<button data-r3-plate="${i}" class="${i===index?'active':''}">${p.label}<small>${p.count} parts · ${p.height.toFixed(1)} mm high</small></button>`).join('')}</div><a class="download plate-download" href="/models/so101/${p.file}" download>Download this plate · 3MF</a>${p.slicer?.gcode_present?`<p class="panel-help">${p.slicer.gcode_summary.map(s=>s.replace(/^; /,'')).join('<br>')}<br>Estimated by Bambu Studio.</p>`:''}<div class="divider"></div><p class="group-title">Prototype print setup</p><p class="panel-help">P1S · 0.4 mm nozzle · PETG<br>0.20 mm layers · 4 walls · 25% gyroid<br>Automatic supports · 5 mm brim<br>12 mm part spacing · 35 mm front reserve</p><p class="notice">Unpowered assembly test first. Nominal MG996R fit is checked in CAD; strength, payload and powered operation are not validated. The leader is still a reference model.</p><p class="panel-help"><a href="${ROOT}READ-ME-FIRST.md" target="_blank">Assembly notes and complete prototype BOM</a><br><a href="${ROOT}SO101-MG996R-R3-PROTOTYPE.zip" download>Download all seven STLs and both plate files</a></p>`;
 const warning=document.createElement('p');warning.className='notice';warning.textContent=toolpathNotice(manifest);
 document.querySelector('.plate-download').after(warning);
 document.querySelector('.plate-download').textContent='Download geometry layout · 3MF';
 document.querySelectorAll('[data-r3-plate]').forEach(b=>b.onclick=()=>onSelect(Number(b.dataset.r3Plate)));
}
export function renderR3Checks(manifest,motion){
 const data=manifest.prototype_reports,parts=data.build.print_units;
 document.querySelector('#checks-view').innerHTML=`<h1>MG996R follower · R3</h1><p>Original SO-101 parts with six tab mounts, six metal-horn interfaces, moving-joint reliefs and an 8 mm wrist extension. Seven joined printing units replace the ten structural source pieces.</p><div class="check-row good"><div>Printable mesh checks<p>${parts.length} closed, positive-volume, single-shell printing units. These are the converted files, not stock SO-101 plates.</p></div></div><div class="check-row good"><div>Nominal attachment checks<p>${data.interfaces.joints.filter(j=>j.insertion_passed&&j.four_tab_lands_present&&j.four_horn_lands_present).length}/6 joints pass hornless insertion, four tab screw lands and four horn screw lands.</p></div></div><div class="check-row pending"><div>Motion checks<p>${r3Notice(motion)} The viewer blocks follower vertices below the tabletop; this is a preview guard, not hardware control.</p></div></div><div class="check-row ${data.plates.sliced?'good':'pending'}"><div>P1S layouts<p>${data.plates.plates.length} plates, 12 mm part spacing. ${data.plates.sliced?'Both plates generated G-code successfully with the supplied P1S/PETG profiles.':'Slicing is not verified yet.'}</p></div></div><div class="check-row pending"><div>Still requires bench validation<p>MG996R single-sided shaft support, PETG load paths, screw access with real tools, cable routing, motor torque and temperature. No payload rating. Encoder leader and electronics enclosure are not completed.</p></div></div><p><a href="${ROOT}READ-ME-FIRST.md" target="_blank">BOM and assembly notes</a> · <a href="${ROOT}motion-check.json" target="_blank">Motion evidence</a> · <a href="${ROOT}interface-check.json" target="_blank">Interface evidence</a></p><h2>Converted printing units</h2><table><thead><tr><th>Part</th><th>Original parts retained</th><th>File</th></tr></thead><tbody>${parts.map(p=>`<tr><td>${p.label}</td><td>${p.source_parts.join(', ')}</td><td><a href="${ROOT}print-parts/${p.file}" download>STL</a></td></tr>`).join('')}</tbody></table>`;
 const layoutRow=[...document.querySelectorAll('#checks-view .check-row')].find(r=>r.textContent.includes('P1S layouts'));
 layoutRow.className='check-row pending';
 layoutRow.querySelector('p').textContent=`${data.plates.plates.length} geometry-only layouts, 12 mm part spacing. ${toolpathNotice(manifest)}`;
}

// Exact transformed mesh-vertex minimum against a planar tabletop. The cheap
// bounding-box rejection avoids scanning vertices unless a mesh is near it.
// This is not a self-collision or continuous-motion solver.
export function followerBelowTable(meshes,tableZ=-.2){
 for(const mesh of meshes){
  if(mesh.userData.robot!=='follower')continue;
  const g=mesh.geometry;if(!g.boundingBox)g.computeBoundingBox();
  const b=g.boundingBox,e=mesh.matrixWorld.elements;
  const min=e[14]+Math.min(e[2]*b.min.x,e[2]*b.max.x)+Math.min(e[6]*b.min.y,e[6]*b.max.y)+Math.min(e[10]*b.min.z,e[10]*b.max.z);
  if(min>=tableZ)continue;
  const a=g.attributes.position;
  for(let k=0;k<a.count;k++)if(e[2]*a.getX(k)+e[6]*a.getY(k)+e[10]*a.getZ(k)+e[14]<tableZ)return true;
 }
 return false;
}
