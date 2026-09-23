from pathlib import Path
import trimesh,numpy as np,json
ROOT=Path(__file__).resolve().parents[2];rows=[]
for p in (ROOT/'solidworks/exports/visual_mm').glob('*_MG996R_R3.stl'):
    if p.stem.startswith('Forearm'):continue
    a=trimesh.load(ROOT/'robot-studio/public/models/so101/follower-r3/print-parts'/p.name);b=trimesh.load(p);ds=[]
    for x,y in [(a,b),(b,a)]:
        pts=np.vstack([x.vertices,trimesh.sample.sample_surface(x,30000,seed=1996)[0]])
        ds.append(float(max(max(trimesh.proximity.closest_point(y,c)[1]) for c in np.array_split(pts,100))))
    r={'part':p.stem,'source_volume_mm3':float(a.volume),'cad_export_volume_mm3':float(b.volume),'bounds_delta_mm':float(np.max(abs(a.bounds-b.bounds))),'relative_volume_delta':float(b.volume/a.volume-1),'bidirectional_all_vertices_and_30000_surface_samples_max_mm':ds}
    r['strict_1_micron_surface_check']=max(ds)<.001
    r['comparison_tolerance_mm']=.005
    r['tolerance_basis']='Current R3 build_follower_r3.py load/export uses 0.005 mm surface simplification. Preserve stricter 1 micron result separately.'
    r['surface_comparison_pass']=max(ds)<r['comparison_tolerance_mm'] and r['bounds_delta_mm']<.001 and abs(r['relative_volume_delta'])<1e-5
    rows.append(r);print(r,flush=True)
(ROOT/'verification/printed_surface_comparison.json').write_text(json.dumps(rows,indent=2))
assert all(r['surface_comparison_pass'] for r in rows)
