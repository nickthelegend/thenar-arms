"""Numerically weld CAD-export tessellation solely for independent collision checks."""
from pathlib import Path
import numpy as np,trimesh,json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'verification/cad_collision_check_meshes';out.mkdir(exist_ok=True)
rows=[]
for p in (ROOT/'solidworks/exports/visual_mm').glob('*.stl'):
    m=trimesh.load(p);groups=[m]
    if p.stem=='Forearm_MG996R_R3':
        center=m.triangles_center;norm=m.face_normals
        capz=np.max(abs(m.triangles[:,:,2]+23),axis=1)<1e-4
        upper=(center[:,2]>-23)&~capz|capz&(norm[:,2]<0)
        capx=(np.max(abs(m.triangles[:,:,0]),axis=1)<1e-4)&~upper
        right=(center[:,0]>0)&~capx|capx&(norm[:,0]<0)
        groups=[m.submesh([np.flatnonzero(mask)],append=True,repair=False) for mask in [upper,~upper&right,~upper&~right]]
    for k,a in enumerate(groups):
        b=a.copy();b.merge_vertices(digits_vertex=5);b.update_faces(b.nondegenerate_faces(height=1e-8));b.update_faces(b.unique_faces());b.remove_unreferenced_vertices()
        row={'part':p.stem,'body':k,'source_mesh_volume_mm3':float(a.volume),'welded_volume_mm3':float(b.volume),'watertight':bool(b.is_watertight),'positive_volume':bool(b.is_volume),'vertex_weld_decimal_places_mm':5,'path':str(out/(p.stem+f'_body{k}.stl'))}
        print(row,flush=True);rows.append(row)
        if b.is_volume:b.export(row['path'],file_type='stl_ascii')
(ROOT/'verification/cad_collision_mesh_preparation.json').write_text(json.dumps(rows,indent=2))
assert all(r['positive_volume'] for r in rows)
