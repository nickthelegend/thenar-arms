"""Re-load R3 STL files and test the actual exported follower assembly."""
import hashlib,json,itertools,math,time
import numpy as np
from build_follower_r3 import DEST,load,transform,context,worlds,matrix,LIMITS,cyl

def main():
    start=time.time();m=json.loads((DEST/'assembly-source.json').read_text())
    instances=[i for i in m['instances'] if i['robot']=='follower']
    ss=[i for i in instances if i['part'].startswith('sts3215')]
    shapes={p['id']:load(DEST/'print-parts'/p['file']) for p in m['conversion_units']}
    body=load(DEST/'MG996R_body_reference.stl')
    # Fill the reference horn's bores to form a conservative all-angle envelope.
    # This cannot grant clearance by holding the rotating M3 holes stationary.
    horn=cyl(5.5,12.2,14.2)+cyl(10,14.2,16.7)
    for i in ss:shapes[i['part']]=body+horn
    cache={};poses=[('home',m['home']),('zero',[0]*6)]
    for j,(lo,hi) in enumerate(LIMITS):
        for k in np.linspace(lo,hi,9):
            q=m['home'].copy();q[j]=float(k);poses.append((f'joint_{j}_{k:g}',q))
    rng=np.random.default_rng(101996)
    for k in range(16):poses.append((f'combined_{k}',[rng.uniform(a,b) for a,b in LIMITS]))
    report={'revision':'R3','physical_tested':False,'continuous_sweep_certified':False,
            'method':'Re-imported exported printed STL / nominal body intersections, >0.5 mm³; all pairs including same-link pairs. Horns use a conservative solid rotational envelope (bores filled). Servo/horn intentional spline engagement is not a collision.',
            'files':{str(p.relative_to(DEST)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((DEST/'print-parts').glob('*.stl'))+[DEST/'MG996R_body_reference.stl',DEST/'metal_horn_reference.stl',DEST/'assembly-source.json']},
            'poses':[]}
    for label,q in poses:
        world=worlds(m,q);ts={i['id']:world[i['node']]@matrix(i) for i in instances}
        hits=[];floor_hits=[]
        for i in instances:
            placed=transform(shapes[i['part']],ts[i['id']])
            if placed.bounding_box()[2]<-.001:
                below=placed.trim_by_plane((0,0,-1),0).volume()
                if below>.5:floor_hits.append({'instance':i['id'],'volume_below_table_mm3':round(below,3)})
        for a,b in itertools.combinations(instances,2):
            rel=np.linalg.inv(ts[a['id']])@ts[b['id']]
            key=(a['part'],b['part'],tuple(np.round(rel,5).ravel()))
            if key not in cache:
                sa=shapes[a['part']];sb=transform(shapes[b['part']],rel)
                aa=np.array(sa.bounding_box()).reshape(2,3);bb=np.array(sb.bounding_box()).reshape(2,3)
                cache[key]=0 if np.any(np.minimum(aa[1],bb[1])-np.maximum(aa[0],bb[0])<=0) else (sa^sb).volume()
            v=cache[key]
            if v>.5:hits.append({'a':a['id'],'b':b['id'],'volume_mm3':round(v,3),'same_link':a['node']==b['node']})
        report['poses'].append({'name':label,'angles_degrees':q,'overlaps':hits,'table_intersections':floor_hits})
        print(label,len(hits),'overlaps',flush=True)
        (DEST/'motion-check.json').write_text(json.dumps(report,indent=2))
    report.update({'seconds':time.time()-start,'tested_poses':len(poses),
                   'failed_poses':sum(bool(p['overlaps']) for p in report['poses']),
                   'table_intersection_poses':sum(bool(p['table_intersections']) for p in report['poses'])})
    (DEST/'motion-check.json').write_text(json.dumps(report,indent=2))
    print('Complete',report['tested_poses'],report['failed_poses'],flush=True)

if __name__=='__main__':main()
