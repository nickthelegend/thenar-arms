"""Independent CAD interference checks for the displayed original-part fit study.

Checks exported STEP solids, not screen appearance. Solid envelope overlaps may
include assumed horn contact: every positive finding is a REVIEW/FAIL, never an
automatic print approval. Sampled poses do not certify continuous swept motion.
"""
from pathlib import Path
from itertools import combinations
import hashlib,json,math,time
import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from clearance_study import ROOT,WEB,OUT,servo,transform,matrix

def bounds(s):
    b=s.BoundingBox();return np.array([[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]])

def main():
    started=time.time();m=json.loads((WEB/'study-manifest.json').read_text())
    parts={p['id']:p for p in m['parts']};nodes={n['id']:n for n in m['nodes']}
    instances=[i for i in m['instances'] if i['robot']=='follower']
    shapes={};mesh_checks=[]
    for i in instances:
        name=i['part']
        if name in shapes:continue
        if name=='MG996R_nominal':s=servo(0);path=None
        else:
            original=name.removesuffix('_draft')
            draft=OUT/'step'/(original+'_MG996R_clearance_DRAFT.step')
            path=draft if name.endswith('_draft') and draft.exists() else ROOT/'source/STEP'/(original+'.step')
            s=cq.importers.importStep(str(path)).val()
        shapes[name]=s
        mesh=trimesh.load(WEB/parts[name]['file'],force='mesh')
        mesh_checks.append({'part':name,'watertight':bool(mesh.is_watertight),'step_valid':s.isValid(),'step_solids':len(s.Solids()),'sha256_stl':hashlib.sha256((WEB/parts[name]['file']).read_bytes()).hexdigest(),'step_file':str(path.relative_to(ROOT)) if path else 'nominal servo BREP generated from documented parameters'})
    local_bounds={p:bounds(s) for p,s in shapes.items()}
    cache={};intersections=0
    def matrices(q):
        world={}
        for n in m['nodes']:
            t=matrix(n)
            if n['joint'] is not None:
                # Separate fixed datum + local-Z revolute node, exactly as the UI.
                r=np.eye(4);r[:3,:3]=Rotation.from_euler('z',q[n['joint']],degrees=True).as_matrix();t=t@r
            world[n['id']]=(world[n['parent']] if n['parent'] else np.eye(4))@t
        return {i['id']:world[i['node']]@matrix(i) for i in instances}
    def check(name,q):
        nonlocal intersections
        mats=matrices(q);hits=[];floor_hits=[];all_bounds=[]
        for i in instances:
            b=local_bounds[i['part']]
            corners=np.array([[x,y,z,1] for x in b[:,0] for y in b[:,1] for z in b[:,2]])
            p=(mats[i['id']]@corners.T).T[:,:3];all_bounds.append([p.min(0),p.max(0)])
            if p[:,2].min()<-.5:floor_hits.append({'part':i['part'],'aabb_low_z_mm':round(float(p[:,2].min()),3)})
        for ia,ib in combinations(instances,2):
            rel=np.linalg.inv(mats[ia['id']])@mats[ib['id']]
            key=(ia['part'],ib['part'],tuple(np.round(rel,5).ravel()))
            if key not in cache:
                a=shapes[ia['part']];b=transform(shapes[ib['part']],rel)
                ab=local_bounds[ia['part']];bb=bounds(b)
                if np.min(np.minimum(ab[1],bb[1])-np.maximum(ab[0],bb[0]))<.001:cache[key]=0
                else:
                    common=a.intersect(b);cache[key]=max(0,float(common.Volume()));intersections+=1
            volume=cache[key]
            if volume>.5:
                hits.append({'a':ia['part'],'a_instance':ia['id'],'b':ib['part'],'b_instance':ib['id'],'volume_mm3':round(volume,3),'same_link':ia['node']==ib['node']})
        result={'name':name,'angles_degrees':[round(float(x),4) for x in q],'positive_volume_overlaps':hits,'conservative_floor_candidates':floor_hits,'assembly_aabb_mm':[np.min(np.array(all_bounds)[:,0],axis=0).tolist(),np.max(np.array(all_bounds)[:,1],axis=0).tolist()]}
        print(name,len(hits),'solid overlap candidates;',len(floor_hits),'floor AABB candidates',flush=True)
        return result
    poses=[('home',m['home']),('zero',[0]*6)]
    for j,(lo,hi) in enumerate(m['limits']):
        for tag,v in [('min',lo),('mid',(lo+hi)/2),('max',hi)]:
            q=m['home'][:];q[j]=v;poses.append((f'joint_{j}_{tag}',q))
    for k,t in enumerate(np.linspace(0,2*math.pi,16,endpoint=False)):
        q=[np.clip(v+math.sin(t+j*.5)*[18,10,12,12,18,9][j],*m['limits'][j]) for j,v in enumerate(m['home'])]
        poses.append((f'demo_{k:02}',q))
    rng=np.random.default_rng(101996)
    for k in range(8):poses.append((f'combined_{k:02}',[rng.uniform(lo,hi) for lo,hi in m['limits']]))
    results=[]
    for name,q in poses:
        results.append(check(name,q))
        (ROOT/'output/motion-progress.json').write_text(json.dumps({'completed':len(results),'total':len(poses),'latest':name}))
    home=results[0];failed=[r for r in results if r['positive_volume_overlaps']]
    report={'status':'NOT PRINT READY','physical_tested':False,'user_reported_servo_travel_degrees':180,
      'manifest_sha256':hashlib.sha256((WEB/'study-manifest.json').read_bytes()).hexdigest(),
      'method':'OpenCascade positive solid intersection volume >0.5 mm³ after local-frame bounding-box overlap >0.001 mm. All follower print/servo pairs included; no same-link exclusions. Conservative nominal servo + circular horn envelope, not measured hardware. Floor tests use bounding boxes only.',
      'limits_degrees':m['limits'],'limits_calibrated':False,'display_base_spacing_mm':m['display_base_spacing_mm'],
      'mesh_checks':mesh_checks,'collisions':{'tested_poses':len(results),'home_interferences':len(home['positive_volume_overlaps']),'failed_sampled_poses':len(failed),'sampled_poses_passed':not failed,'full_envelope_passed':False,'home_details':home['positive_volume_overlaps'],'poses':results},
      'leader_status':'Original leader moves kinematically with follower. Encoder fit, trigger alignment and leader collision envelope not certified.',
      'print_release_blockers':['Rejected wrist motor holder: source part remains in preview, MG996R conversion missing.','Open STL seams listed in mesh_checks.','Any positive-volume overlap above is unresolved; inspect exact pair and pose.','Mounting-tab fasteners, horn interfaces, opposite-side support, walls and cable paths remain incomplete.','Actual servo and horn measurements, load/temperature tests and one-joint physical fit test required.'],
      'exact_boolean_evaluations':intersections,'seconds':round(time.time()-started,2)}
    (ROOT/'output/motion-verification.json').write_text(json.dumps(report,indent=2));(WEB/'motion-verification.json').write_text(json.dumps(report,indent=2))
    print('DONE',len(results),'poses;',len(failed),'failed; home:',len(home['positive_volume_overlaps']),'; seconds',report['seconds'],flush=True)

if __name__=='__main__':main()
