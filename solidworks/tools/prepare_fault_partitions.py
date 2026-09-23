"""Section source solids at CAD fault planes, with no removed material."""
from pathlib import Path
import manifold3d as mf,numpy as np,trimesh,json,sys
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'solidworks/checkpoints/import_transport'
name=sys.argv[1]
if name=='forearm':src=out/'Leader_forearm_upper.stl';plane=[0,0,1];offset=16.2;prefix='Leader_forearm_upper_z'
elif name=='forearm_x':src=out/'Leader_forearm_upper_z0.stl';plane=[1,0,0];offset=66.5;prefix='Leader_forearm_tip_x'
elif name=='trigger':src=ROOT/'so101-mg996r/output/encoder-leader-l1/print-parts/Trigger_Encoder_L1.stl';plane=[0,0,1];offset=6.;prefix='Leader_trigger_z'
elif name=='base':src=ROOT/'solidworks/checkpoints/leader_transport/Base_Encoder_L1.stl';plane=[1,0,0];offset=-4.;prefix='Leader_base_x'
else:raise ValueError(name)
m=trimesh.load(src);solid=mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)));assert solid.status()==mf.Error.NoError
rows=[]
for k,b in enumerate(solid.split_by_plane(plane,offset)):
    b=b.simplify(.0001);raw=b.to_mesh64();mesh=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True);path=out/(prefix+str(k)+'.stl');mesh.export(path);rows.append({'name':path.stem,'volume_mm3':mesh.volume,'faces':len(mesh.faces),'plane':plane,'offset_mm':offset})
assert abs(sum(r['volume_mm3'] for r in rows)/m.volume-1)<1e-5
(ROOT/'solidworks/evidence'/(prefix+'_inputs.json')).write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
