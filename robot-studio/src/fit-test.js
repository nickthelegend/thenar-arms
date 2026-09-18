// Test prints are separate plate-only objects, never inserted into the arm
// or allowed to invalidate/misrepresent the existing assembly collision report.
export function addFitTestPlates(manifest, report) {
 if(!report?.parts?.length || !report.parts.every(p=>p.watertight&&p.single_closed_shell&&p.valid_brep))throw new Error('Fit-test mesh validation missing');
 const labels=['Wrist holder · bench test only','MG996R body / tab gauge','Optional horn pattern gauge'];
 report.parts.forEach((p,i)=>manifest.parts.push({id:p.id,label:labels[i],kind:'test',file:'fit-test/'+p.file,bounds:p.bounds_mm[1].map((v,k)=>v-p.bounds_mm[0][k]),watertight:p.watertight,notes:'Unpowered fit test only; not approved for installation in the arm.'}));
 const entries=report.parts.map(p=>({part:p.id,matrix:p.placement_matrix}));
 const plates=[
  {id:'P1S_QUICK_GAUGES_ONLY',label:'Start here: quick fit gauges',entries:entries.slice(1),count:2,height:4},
  {id:'P1S_FIT_TEST_ONLY',label:'Wrist-holder bench test + gauges',entries,count:3,height:Math.max(...report.parts.map(p=>p.placed_bounds_mm[1][2]))}
 ].map(p=>({...p,fitTest:true,robot:'follower',file:'fit-test/'+p.id+'.3mf',slicer:report.slicer?.plates.find(s=>s.plate===p.id)}));
 manifest.plates.unshift(...plates);
 return manifest;
}
