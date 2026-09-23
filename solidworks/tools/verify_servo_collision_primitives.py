"""Independent envelope check for the URDF's simple servo collision shapes."""
from pathlib import Path
import numpy as np,trimesh,manifold3d as mf,json
ROOT=Path(__file__).resolve().parents[2]
shapes=[mf.Manifold.cube((40.9,20,37),True).translate((2.05,0,-10)),mf.Manifold.cube((54,20,2.6),True).translate((2.05,0,-.4)),mf.Manifold.cylinder(3,6.5,circular_segments=1024).translate((12.5,0,8.5)),mf.Manifold.cylinder(5.7,3,circular_segments=1024).translate((12.5,0,8.5))]
s=mf.Manifold.batch_boolean(shapes,mf.OpType.Add);raw=s.to_mesh64();b=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True);a=trimesh.load(ROOT/'solidworks/exports/visual_mm/MG996R_Nominal_R3.stl');dist=[]
for x,y in [(a,b),(b,a)]:
    pts=np.vstack([x.vertices,trimesh.sample.sample_surface(x,12000,seed=996)[0]]);vals=[]
    for k in range(0,len(pts),100):vals.extend(trimesh.proximity.closest_point(y,pts[k:k+100])[1])
    dist.append(max(vals))
row={'representation':'Union of two boxes and two cylinders using native source dimensions','comparison_mesh_cylinder_segments':1024,'bidirectional_sampled_envelope_error_mm':dist,'CAD_tessellation_volume_mm3':a.volume,'primitive_union_volume_mm3':b.volume,'bounds_delta_mm':float(np.max(abs(a.bounds-b.bounds))),'pass':max(dist)<.005 and np.max(abs(a.bounds-b.bounds))<.001,'physical_mass_inertia':'No values inferred from these collision shapes'}
row['pass']=bool(row['pass']);(ROOT/'verification/servo_collision_primitives.json').write_text(json.dumps(row,indent=2));print(json.dumps(row,indent=2));assert row['pass']
