"""Independent checks of exported leader assembly, PCB, bearing and magnet fits."""
import json,hashlib,itertools,math
import numpy as np
from scipy.spatial.transform import Rotation
from build_encoder_leader import DEST,context,DRIVEN,UNITS,OWNERS
from build_follower_r3 import load,transform,matrix,worlds,cyl,box

def main():
    build=json.loads((DEST/'build-report.json').read_text());enc=json.loads((DEST/'encoder-build.json').read_text())
    m=json.loads((DEST/'assembly-source.json').read_text());w=worlds(m)
    ss=[i for i in m['instances'] if i['part'].startswith('sts3215')]
    m['instances']=[i for i in m['instances'] if not i['part'].startswith('sts3215')]
    rows=build['print_units']+enc['parts'];shapes={};paths={}
    for p in rows:
        path=DEST/('reference' if p.get('kind')=='hardware' else 'print-parts')/p['file']
        shapes[p['id']]=load(path);paths[str(path.relative_to(DEST))]=hashlib.sha256(path.read_bytes()).hexdigest()
    child_units={p:name+'_Encoder_L1' for name,members in UNITS.items() for p in members}
    for j,s in enumerate(ss):
        child=next(i for i in m['instances'] if i['part']==child_units[DRIVEN[j]])
        for p in enc['parts']:
            node=child['node'] if p['id'] in ['Encoder_rotor_L1','Magnet_cup_L1','Diametric_magnet_L1'] else s['node']
            t=np.linalg.inv(w[node])@w[s['node']]@matrix(s)
            m['instances'].append({'id':f'encoder_{j}_{p["id"]}','part':p['id'],'node':node,'robot':'follower',
                'position':t[:3,3].tolist(),'rotation':Rotation.from_matrix(t[:3,:3]).as_euler('XYZ',degrees=True).tolist(),'joint_index':j})
    # Interference tests in the actual assembly; no same-link suppression.
    poses=[('home',m['home']),('zero',[0]*6)]
    for j,(lo,hi) in enumerate(m['limits']):
        for v in np.linspace(lo,hi,9):q=m['home'].copy();q[j]=float(v);poses.append((f'joint_{j}_{v:g}',q))
    rng=np.random.default_rng(5600)
    for j in range(16):poses.append((f'combined_{j}',[float(rng.uniform(a,b)) for a,b in m['limits']]))
    cache={};results=[];instances=m['instances']
    for label,q in poses:
        ws=worlds(m,q);placed={i['id']:transform(shapes[i['part']],ws[i['node']]@matrix(i)) for i in instances}
        ts={i['id']:ws[i['node']]@matrix(i) for i in instances};hits=[];table=[]
        bounds={key:np.array(s.bounding_box()).reshape(2,3) for key,s in placed.items()}
        for i in instances:
            if bounds[i['id']][0,2]<-.01:
                v=placed[i['id']].trim_by_plane((0,0,-1),0).volume()
                if v>.5:table.append({'part':i['id'],'mm3':v})
        for a,c in itertools.combinations(instances,2):
            aa,bb=bounds[a['id']],bounds[c['id']]
            if np.any(np.minimum(aa[1],bb[1])-np.maximum(aa[0],bb[0])<=0):continue
            t=np.linalg.inv(ts[a['id']])@ts[c['id']];key=(a['part'],c['part'],tuple(np.round(t,5).ravel()))
            if key not in cache:cache[key]=max(0,(shapes[a['part']]^transform(shapes[c['part']],t)).volume())
            if cache[key]>.5:hits.append({'a':a['id'],'b':c['id'],'mm3':round(cache[key],3)})
        results.append({'name':label,'angles_degrees':q,'overlaps':hits,'table_intersections':table})
    # One reusable cartridge, checked independently of its link surroundings.
    frame=shapes['Encoder_cartridge_L1'];pcb=shapes['AS5600_PCB_L1']
    board=pcb+shapes['AS5600_chip_L1']+shapes['AS5600_connectors_L1']
    pcb_insertion=[max(0,(frame^board.translate((0,float(y),0))).volume()) for y in np.linspace(0,35,36)]
    rotation_checks=[]
    for a in range(0,360,5):
        t=np.eye(4);t[:3,:3]=Rotation.from_euler('z',a,degrees=True).as_matrix();t[:3,3]=np.array([12.5,0,0])-t[:3,:3]@np.array([12.5,0,0])
        moving=transform(shapes['Encoder_rotor_L1']+shapes['Magnet_cup_L1']+shapes['Diametric_magnet_L1'],t)
        fixed=frame+shapes['Bearing_cap_front_L1']+shapes['Bearing_cap_rear_L1']+shapes['AS5600_chip_L1']+pcb+shapes['688_bearing_front_L1']+shapes['688_bearing_rear_L1']
        rotation_checks.append(max(0,(moving^fixed).volume()))
    magnet_bottom=shapes['Diametric_magnet_L1'].bounding_box()[2];chip_top=shapes['AS5600_chip_L1'].bounding_box()[5]
    _,_,ps,sm,pm=context();interfaces=[]
    by_source={source:p for p in build['print_units'] for source in p['source_parts']}
    for j,(owner,driven) in enumerate(zip(OWNERS,DRIVEN)):
        h=by_source[owner];d=by_source[driven]
        holder=transform(shapes[h['id']],np.linalg.inv(sm[j])@pm[h['anchor_source_frame']])
        child=transform(shapes[d['id']],np.linalg.inv(sm[j])@pm[d['anchor_source_frame']])
        insertion=[max(0,(holder^frame.translate((0,0,float(z)))).volume()) for z in np.linspace(0,65,27)]
        lands=[(holder^cyl(3.5,-5.6,-1.8,x,y)).volume()/3.8 for x in [-22.7,32.8] for y in [-5,5]]
        shanks=[max(0,(holder^cyl(1.5,-10,1.5,x,y)).volume()) for x in [-22.7,32.8] for y in [-5,5]]
        horn_lands=[(child^cyl(3.2,16.8,22.6,12.5+x,y)).volume()/5.8 for x,y in [(7,0),(-7,0),(0,7),(0,-7)]]
        interfaces.append({'joint':j,'insertion_max_mm3':max(insertion),'tab_lands_mm2':lands,'tab_shank_overlap_mm3':shanks,
            'rotor_screw_lands_mm2':horn_lands,'passed':max(insertion)<.5 and min(lands)>=12 and max(shanks)<.05 and min(horn_lands)>=12})
    report={'revision':'L1','physical_tested':False,'files':paths,'poses':results,'tested_poses':len(results),
        'failed_poses':sum(bool(p['overlaps']) for p in results),'table_intersection_poses':sum(bool(p['table_intersections']) for p in results),
        'cartridge_rotation_max_overlap_mm3':max(rotation_checks),'pcb_insertion_max_overlap_mm3':max(pcb_insertion),
        'interfaces':interfaces,'all_interfaces_passed':all(i['passed'] for i in interfaces),
        'magnet_chip_gap_mm':magnet_bottom-chip_top,'method':'Exported meshes reloaded; all pair intersections >0.5 mm³ reported. 72 full-arm poses, 72 cartridge rotor samples, 36 assembled-PCB slide-in samples, six cartridge insertion/tab-land/rotor-land checks. No wires or threaded screw engagement simulation.',
        'remaining':['Physical bearing journal fit','Magnetic field strength/status and zero/sign calibration','Cable bend and fastener/tool clearance under actual assembly load']}
    (DEST/'verification.json').write_text(json.dumps(report,indent=2));(DEST/'assembly.json').write_text(json.dumps(m,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['files','poses','interfaces','remaining','method']},indent=2))
    print('Failed pose names:',[p['name'] for p in results if p['overlaps']]);print('Interfaces:',[(i['joint'],i['passed']) for i in interfaces])

if __name__=='__main__':main()
