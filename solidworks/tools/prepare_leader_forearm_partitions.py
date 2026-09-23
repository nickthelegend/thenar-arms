from pathlib import Path
import manifold3d as mf,trimesh,numpy as np,json
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'so101-mg996r/output/encoder-leader-l1/print-parts/Forearm_Encoder_L1.stl';mesh=trimesh.load(source)
solid=mf.Manifold(mf.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),np.asarray(mesh.faces,dtype=np.uint64)));assert solid.status()==mf.Error.NoError
upper,lower=solid.split_by_plane((0,0,1),-23);right,left=lower.split_by_plane((1,0,0),0)
out=ROOT/'solidworks/checkpoints/import_transport';rows=[]
for name,b in [('Leader_forearm_upper',upper),('Leader_forearm_lower_right',right),('Leader_forearm_lower_left',left)]:
    original_volume=b.volume();b=b.simplify(.0001);raw=b.to_mesh64();m=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True);path=out/(name+'.stl');m.export(path);assert m.is_volume
    rows.append({'name':name,'source':str(source),'path':str(path),'volume_mm3':m.volume,'before_simplify_volume_mm3':original_volume,'faces':len(m.faces),'conditioning':'Manifold simplify 0.0001mm after exact Z=-23 and lower X=0 sectioning; exterior comparison pending'})
assert abs(sum(r['volume_mm3'] for r in rows)/mesh.volume-1)<1e-5
(ROOT/'solidworks/evidence/leader_forearm_partition_inputs.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
