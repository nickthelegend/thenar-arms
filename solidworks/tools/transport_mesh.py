"""Bounded numerical conditioning of failed STL imports, never original file edits."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh,pymeshfix
ROOT=Path(__file__).resolve().parents[2]
def main(name):
    src=ROOT/'robot-studio/public/models/so101/follower-r3/print-parts'/(name+'_MG996R_R3.stl')
    orig=trimesh.load(src,force='mesh');work=orig.copy()
    # SW's metre-space import tolerance loses extremely short STL edges.
    work.merge_vertices(digits_vertex=4)
    work.update_faces(work.nondegenerate_faces(height=1e-7));work.update_faces(work.unique_faces());work.remove_unreferenced_vertices()
    fix=pymeshfix.MeshFix(work.vertices,work.faces)
    fix.repair(joincomp=False,remove_smallest_components=False)
    repaired=trimesh.Trimesh(fix.points,fix.faces,process=True)
    dest=ROOT/'solidworks/checkpoints/import_transport'/src.name
    repaired.export(dest);actual=trimesh.load(dest,force='mesh')
    distances=[]
    for a,b in [(orig,actual),(actual,orig)]:
        pts=np.vstack([a.vertices,trimesh.sample.sample_surface(a,30000,seed=101996)[0]])
        ds=[]
        for chunk in np.array_split(pts,50):ds.extend(trimesh.proximity.closest_point(b,chunk)[1])
        distances.append(float(max(ds)))
    evidence={'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source':str(src),'transport':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'watertight':bool(actual.is_watertight),'positive_volume':bool(actual.is_volume),'shells':len(actual.split()),'relative_volume_change':float(abs(actual.volume/orig.volume-1)),'bounds_delta_mm':float(np.max(abs(actual.bounds-orig.bounds))),'bidirectional_vertex_and_30000_surface_sample_distance_mm':distances,'conditioning':'merge at 0.0001mm rounding, remove collapsed facets, repair residual topology; original untouched','status':'REJECTED'}
    passed=actual.is_watertight and actual.is_volume and len(actual.split())==1 and evidence['relative_volume_change']<1e-5 and max(distances)<.001 and evidence['bounds_delta_mm']<.001
    if passed:evidence['status']='ACCEPTED as numerical import transport only; CAD remeasurement required'
    (ROOT/'solidworks/evidence'/(name+'_transport.json')).write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence),flush=True)
    assert passed,'Transport exceeds preservation gate'
if __name__=='__main__':
    import sys;main(sys.argv[1])
