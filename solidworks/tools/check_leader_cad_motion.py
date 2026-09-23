"""All-pair discrete volumetric intersections at measured native leader poses."""
from pathlib import Path
from itertools import combinations
import json,numpy as np,trimesh,manifold3d as mf,time
ROOT=Path(__file__).resolve().parents[2]
m=json.loads((ROOT/'robot-studio/public/models/so101/study-manifest.json').read_text());inst={i['id']:i for i in m['instances'] if i['robot']=='leader'}
shapes={};meshes={}
for r in json.loads((ROOT/'verification/leader_collision_mesh_preparation.json').read_text()):
    assert r['positive_volume'];mesh=trimesh.load(r['path']);shape=mf.Manifold(mf.Mesh64(np.asarray(mesh.vertices),np.asarray(mesh.faces,dtype=np.uint64)));assert shape.status()==mf.Error.NoError,(r,shape.status())
    shapes.setdefault(r['part'],[]).append(shape);meshes.setdefault(r['part'],[]).append(mesh)
poses=json.loads((ROOT/'solidworks/evidence/leader_joint_motion_measurements.json').read_text());cache={};results=[];started=time.time()
for pose in poses:
    if 'ZERO_AFTER' in pose['name'] or pose['name']=='ZERO_FINAL':continue
    mats={r['id']:np.array(r['measured_transform_mm']) for r in pose['components']};hits=[];table=[];bb={}
    for name,t in mats.items():
        pts=np.vstack([a.vertices for a in meshes[inst[name]['part']]]);world=trimesh.transform_points(pts,t);bb[name]=np.array([world.min(0),world.max(0)])
        if world[:,2].min()<-.001:table.append({'id':name,'lowest_vertex_z_mm':float(world[:,2].min())})
    for ia,ib in combinations(mats,2):
        if np.any(np.minimum(bb[ia][1],bb[ib][1])-np.maximum(bb[ia][0],bb[ib][0])<=1e-6):continue
        pa=inst[ia]['part'];pb=inst[ib]['part'];rel=np.linalg.inv(mats[ia])@mats[ib];key=(pa,pb,tuple(np.round(rel,8).ravel()))
        if key not in cache:
            volume=0
            for a in shapes[pa]:
                for b in shapes[pb]:
                    c=a^b.transform(rel[:3,:]);assert c.status()==mf.Error.NoError,(ia,ib,c.status());volume+=max(0,c.volume())
            cache[key]=volume
        if cache[key]>1e-5:hits.append({'a':ia,'b':ib,'volume_mm3':cache[key],'same_rigid_link':inst[ia]['node']==inst[ib]['node'],'above_source_report_threshold':cache[key]>.5})
    results.append({'pose':pose['name'],'joint_degrees':pose['command_deg'],'intersections':hits,'table_penetrations':table})
    out={'method':'All component pairs of individually exported SolidWorks solid bodies at 73 measured mate-solved transforms. 0.00001 mm tessellation vertex welding. Source zero-thickness surface artifacts have no volume and are excluded here, retained in visual comparison. Discrete poses, not swept-motion certification.','volume_reporting_threshold_mm3':1e-5,'source_significance_threshold_mm3':.5,'tested_poses':results,'relative_pair_cache_count':len(cache),'elapsed_seconds':time.time()-started}
    (ROOT/'verification/leader_cad_mesh_motion_interference.json').write_text(json.dumps(out,indent=2));print(pose['name'],'hits',len(hits),'above0.5',sum(h['above_source_report_threshold'] for h in hits),'table',len(table),'seconds',round(time.time()-started,1),flush=True)
