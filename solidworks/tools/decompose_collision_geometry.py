"""Convex collision proxies from accepted CAD meshes; dimensions remain in metres."""
from pathlib import Path
import coacd,numpy as np,trimesh,json,sys,time
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'simulation/collision_convex';out.mkdir(exist_ok=True)
coacd.set_log_level('info');rows=[]
record=out/'manifest.json'
if record.exists():rows=json.loads(record.read_text())
for entry in json.loads((ROOT/'verification/cad_collision_mesh_preparation.json').read_text()):
    key=entry['part']+f"_body{entry['body']}"
    if len(sys.argv)>1 and sys.argv[1] not in key:continue
    if any(r['key']==key for r in rows):continue
    mesh=trimesh.load(entry['path']);assert mesh.is_volume
    print('Decompose',key,flush=True);started=time.time()
    hulls=coacd.run_coacd(coacd.Mesh(np.asarray(mesh.vertices),np.asarray(mesh.faces)),threshold=.1,real_metric=True,preprocess_mode='off',resolution=1000,mcts_nodes=4,mcts_iterations=10,mcts_max_depth=2,merge=True,decimate=False,extrude=False,seed=101996)
    files=[]
    for k,(v,f) in enumerate(hulls):
        h=trimesh.Trimesh(v,f,process=True);h.apply_scale(.001);assert h.is_volume and h.is_convex
        path=out/(key+f'_convex{k:03}.stl');h.export(path);files.append(path.name)
    row={'key':key,'part':entry['part'],'body':entry['body'],'input_CAD_closed_mesh':entry['path'],'units':'metres','method':'CoACD 1.0.14, no voxel preprocessing or extrusion','requested_concavity_m':.0001,'convex_files':files,'seconds':time.time()-started,'acceptance':'PENDING independent envelope comparison'}
    rows.append(row);record.write_text(json.dumps(rows,indent=2));print(key,len(files),'hulls',round(row['seconds'],1),'seconds',flush=True)
