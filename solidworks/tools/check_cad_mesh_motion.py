"""Independent intersections of CAD-exported closed meshes at measured assembly poses."""
from pathlib import Path
from itertools import combinations
import json,numpy as np,trimesh,manifold3d as mf,time
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'robot-studio/public/models/so101/study-manifest.json').read_text())
inst={i['id']:i for i in manifest['instances'] if i['robot']=='follower'}
part_map={'MG996R_body_R3':'MG996R_Nominal_R3','metal_horn_R3':'Metal_Horn_D20_PCD14_R3'}
shapes={};meshes={};prep=json.loads((ROOT/'verification/cad_collision_mesh_preparation.json').read_text())
for r in prep:
    assert r['positive_volume'];m=trimesh.load(r['path']);s=mf.Manifold(mf.Mesh64(np.asarray(m.vertices),np.asarray(m.faces,dtype=np.uint64)))
    assert s.status()==mf.Error.NoError,(r,s.status());shapes.setdefault(r['part'],[]).append(s);meshes.setdefault(r['part'],[]).append(m)
poses=json.loads((ROOT/'solidworks/evidence/joint_motion_measurements.json').read_text());cache={};results=[];started=time.time()
for pose in poses:
    if 'ZERO_AFTER' in pose['name'] or pose['name']=='ZERO_FINAL':continue
    mats={r['id']:np.array(r['measured_transform_mm']) for r in pose['components']};hits=[];table=[];bb={}
    for id,t in mats.items():
        part=part_map.get(inst[id]['part'],inst[id]['part']);pts=np.vstack([m.vertices for m in meshes[part]]);world=trimesh.transform_points(pts,t);bb[id]=np.array([world.min(0),world.max(0)])
        if world[:,2].min()<-.001:table.append({'id':id,'lowest_vertex_z_mm':float(world[:,2].min())})
    for ia,ib in combinations(mats,2):
        if np.any(np.minimum(bb[ia][1],bb[ib][1])-np.maximum(bb[ia][0],bb[ib][0])<=1e-6):continue
        pa=part_map.get(inst[ia]['part'],inst[ia]['part']);pb=part_map.get(inst[ib]['part'],inst[ib]['part']);rel=np.linalg.inv(mats[ia])@mats[ib]
        key=(pa,pb,tuple(np.round(rel,8).ravel()))
        if key not in cache:
            volume=0
            for a in shapes[pa]:
                for b in shapes[pb]:
                    c=a^b.transform(rel[:3,:]);assert c.status()==mf.Error.NoError,(ia,ib,c.status());volume+=max(0,c.volume())
            cache[key]=volume
        if cache[key]>1e-5:hits.append({'a':ia,'b':ib,'volume_mm3':cache[key],'same_rigid_link':inst[ia]['node']==inst[ib]['node'],'above_source_report_threshold':cache[key]>.5})
    row={'pose':pose['name'],'joint_degrees':pose['command_deg'],'intersections':hits,'table_penetrations':table};results.append(row)
    out={'method':'Manifold3D intersections of SolidWorks-exported closed CAD tessellation, 0.00001 mm vertex welding, at 19 measured mate-solved transforms. Forearm three solid regions retained independently. All component pairs included, no intentional-intersection exclusions. Discrete poses, not swept-motion certification.','volume_reporting_threshold_mm3':1e-5,'source_significance_threshold_mm3':.5,'tested_poses':results,'relative_pair_cache_count':len(cache),'elapsed_seconds':time.time()-started}
    (ROOT/'verification/cad_mesh_motion_interference.json').write_text(json.dumps(out,indent=2))
    print(pose['name'],'hits',len(hits),'above 0.5',sum(h['above_source_report_threshold'] for h in hits),'table',len(table),'seconds',round(time.time()-started,1),flush=True)
