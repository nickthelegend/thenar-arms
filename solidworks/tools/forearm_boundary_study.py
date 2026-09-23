"""Study source coincident opposing facets; candidates remain unaccepted until checked."""
from pathlib import Path
import json,numpy as np,trimesh,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
def clean(m):
    m.merge_vertices(digits_vertex=6)
    m.update_faces(m.nondegenerate_faces(height=1e-9));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices();return m
def main():
    orig=trimesh.load(ROOT/'robot-studio/public/models/so101/follower-r3/print-parts/Forearm_MG996R_R3.stl')
    on=np.max(abs(orig.triangles[:,:,2]+23),axis=1)<1e-6
    areas=[]
    for sign in [1,-1]:
        triangles=orig.triangles[on&(orig.face_normals[:,2]*sign>0)]
        areas.append(unary_union([shapely.set_precision(Polygon(t[:,:2]),1e-7) for t in triangles]))
    ps=areas[0].difference(areas[1]);ns=areas[1].difference(areas[0]);out=[orig.triangles[~on]]
    for region,sign in [(ps,1),(ns,-1)]:
        for poly in shapely.get_parts(shapely.constrained_delaunay_triangles(region)):
            pts=np.asarray(poly.exterior.coords)[:3];xyz=np.c_[pts,np.full(3,-23.)]
            if np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])[2]*sign<0:xyz=xyz[::-1]
            out.append(xyz[None,:,:])
    ts=np.vstack(out);m=clean(trimesh.Trimesh(ts.reshape(-1,3),np.arange(len(ts)*3).reshape(-1,3),process=False))
    # Preserve source boundary tessellation when a merged planar edge spans old vertices.
    for iteration in range(4):
        counts=np.bincount(m.edges_unique_inverse);boundary=m.edges_unique[counts==1];bv=np.unique(boundary)
        if not len(boundary):break
        changes={}
        for edge in boundary:
            a,b=m.vertices[edge];v=b-a;l=np.dot(v,v)
            if l<1e-16:continue
            candidates=m.vertices[bv];t=(candidates-a)@v/l;dist=np.linalg.norm(candidates-(a+t[:,None]*v),axis=1)
            inds=np.where((dist<2e-6)&(t>1e-7)&(t<1-1e-7))[0]
            if len(inds):changes[tuple(edge)]=bv[inds[np.argsort(t[inds])]].tolist()
        if not changes:break
        faces=[]
        for face in m.faces:
            did=False
            for a,b,c in [(face[0],face[1],face[2]),(face[1],face[2],face[0]),(face[2],face[0],face[1])]:
                key=tuple(sorted([a,b]))
                if key in changes:
                    mid=changes[key] if a==key[0] else changes[key][::-1];chain=[a]+mid+[b]
                    faces.extend([[chain[k],chain[k+1],c] for k in range(len(chain)-1)]);did=True;break
            if not did:faces.append(face)
        m=clean(trimesh.Trimesh(m.vertices,faces,process=False))
    counts=np.bincount(m.edges_unique_inverse)
    path=ROOT/'solidworks/checkpoints/import_transport/Forearm_boundary_candidate.stl';m.export(path,file_type='stl_ascii')
    row={'status':'STUDY ONLY; not accepted as geometry','opposing_coplanar_area_mm2':areas[0].intersection(areas[1]).area,'source_plane_z_mm':-23,'source_plane_faces':int(sum(on)),'candidate_watertight':bool(m.is_watertight),'candidate_positive_volume':bool(m.is_volume),'volume_relative_delta':float(m.volume/orig.volume-1),'bounds_delta_mm':float(np.max(abs(m.bounds-orig.bounds))),'edge_incidence_histogram':{str(k):int(v) for k,v in zip(*np.unique(counts,return_counts=True))},'path':str(path)}
    (ROOT/'solidworks/evidence/Forearm_boundary_study.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
if __name__=='__main__':main()
