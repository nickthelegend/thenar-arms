"""Compare the partitioned CAD forearm with the published source exterior."""
from pathlib import Path
import trimesh,numpy as np,json
ROOT=Path(__file__).resolve().parents[2]
a=trimesh.load(ROOT/'robot-studio/public/models/so101/follower-r3/print-parts/Forearm_MG996R_R3.stl')
b=trimesh.load(ROOT/'solidworks/checkpoints/import_transport/Forearm_seam_CAD_export.stl')
source_pts=np.vstack([a.vertices,trimesh.sample.sample_surface(a,50000,seed=1996)[0]])
def distances(mesh,pts):return np.concatenate([trimesh.proximity.closest_point(mesh,c)[1] for c in np.array_split(pts,100)])
source_to_cad=distances(b,source_pts)
# Added section faces lie only in these exact partition planes. Exterior faces
# coplanar with these planes are still covered by the full source-to-CAD test.
seams=(np.max(abs(b.triangles[:,:,2]+23),axis=1)<1e-4)|((np.max(abs(b.triangles[:,:,0]),axis=1)<1e-4)&(np.max(b.triangles[:,:,2],axis=1)<-22.9999))
exterior=b.submesh([np.flatnonzero(~seams)],append=True,repair=False)
cad_pts=np.vstack([exterior.vertices,trimesh.sample.sample_surface(exterior,50000,seed=1996)[0]])
cad_to_source=distances(a,cad_pts)
ev={'representation':'Three nonoverlapping closed CAD bodies in one rigid part. Extra partition faces at Z=-23 mm and X=0 below Z=-23 mm; native union failed.','source_volume_mm3':float(a.volume),'cad_export_signed_volume_sum_mm3':float(b.volume),'relative_volume_delta':float(b.volume/a.volume-1),'bounds_max_delta_mm':float(np.max(abs(b.bounds-a.bounds))),'source_all_vertices_and_50000_samples_to_cad_max_mm':float(source_to_cad.max()),'cad_exterior_vertices_and_50000_samples_to_source_max_mm':float(cad_to_source.max()),'excluded_partition_triangles':int(seams.sum()),'export_triangles':len(b.faces),'status':'PENDING'}
passed=abs(ev['relative_volume_delta'])<1e-5 and ev['bounds_max_delta_mm']<.001 and max(source_to_cad.max(),cad_to_source.max())<.001
ev['status']='ACCEPTED bounded geometric preservation as partitioned solid part; not a single fused CAD body' if passed else 'REJECTED'
(ROOT/'solidworks/evidence/Forearm_seam_comparison.json').write_text(json.dumps(ev,indent=2));print(json.dumps(ev,indent=2),flush=True)
assert passed,ev
