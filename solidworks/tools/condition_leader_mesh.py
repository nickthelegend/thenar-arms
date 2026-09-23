"""Make a bounded STL transport copy for a failed L1 CAD import."""
from pathlib import Path
import numpy as np,trimesh,pymeshfix,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[2]
name=sys.argv[1];src=ROOT/'so101-mg996r/output/encoder-leader-l1/print-parts'/(name+'.stl');a=trimesh.load(src);m=a.copy()
m.merge_vertices(digits_vertex=4);m.update_faces(m.nondegenerate_faces(height=1e-7));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
fix=pymeshfix.MeshFix(m.vertices,m.faces);fix.repair(joincomp=False,remove_smallest_components=False);b=trimesh.Trimesh(fix.points,fix.faces,process=True)
out=ROOT/'solidworks/checkpoints/leader_transport';out.mkdir(exist_ok=True);path=out/src.name;b.export(path);b=trimesh.load(path)
errors=[]
for x,y in [(a,b),(b,a)]:
    points=np.vstack([x.vertices,trimesh.sample.sample_surface(x,30000,seed=1015600)[0]]);dist=[]
    for chunk in np.array_split(points,50):dist.extend(trimesh.proximity.closest_point(y,chunk)[1])
    errors.append(float(max(dist)))
row={'part':name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'transport':str(path),'watertight':bool(b.is_volume),'shells':len(b.split()),'relative_volume_error':float(abs(b.volume/a.volume-1)),'bounds_delta_mm':float(np.max(abs(b.bounds-a.bounds))),'sampled_bidirectional_error_mm':errors,'method':'0.0001mm coordinate weld, collapsed-face cleanup and bounded MeshFix; source unchanged'}
row['accepted_transport']=row['watertight'] and row['shells']==1 and row['relative_volume_error']<1e-5 and row['bounds_delta_mm']<.001 and max(errors)<.001
(ROOT/'solidworks/evidence'/(name+'_transport.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
assert row['accepted_transport'],row
