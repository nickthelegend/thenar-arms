"""Fetch the requested original files without rewriting a single mesh byte.

Run with mg996r-arm/.venv/bin/python so101-mg996r/tools/import_sources.py.
The viewer uses original STL geometry and upstream URDF joint datums (mm).
"""
from pathlib import Path
import concurrent.futures, hashlib, json, shutil, urllib.request, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent/'SO-ARM100'
WEB=ROOT.parent/'robot-studio/public/models/so101'
COMMIT='eecbe3e0a9ebb23e25ad7b2759b03884c6660903'
COMMON=['Base_motor_holder_SO101','Base_SO101','Motor_holder_SO101_Base','Motor_holder_SO101_Wrist','Under_arm_SO101','Upper_arm_SO101','Rotation_Pitch_SO101','Wrist_Roll_Pitch_SO101','WaveShare_Mounting_Plate_SO101']
LEADER=['Handle_SO101','Trigger_SO101','Wrist_Roll_SO101']
FOLLOWER=['Moving_Jaw_SO101','Wrist_Roll_Follower_SO101']
NAMES=COMMON+LEADER+FOLLOWER
for d in ['source/Individual','source/Follower','source/Leader','source/STEP','output','tools']:(ROOT/d).mkdir(parents=True,exist_ok=True)
WEB.mkdir(parents=True,exist_ok=True)

def fetch(rel):
    url=f'https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/{COMMIT}/STL/SO101/{rel}'
    dest=ROOT/'source'/rel
    if not dest.exists():
        with urllib.request.urlopen(url,timeout=120) as r: data=r.read()
        dest.write_bytes(data)
    data=dest.read_bytes()
    local=(REPO/'STL/SO101'/rel).read_bytes()
    assert data==local, f'Upstream changed: {rel}'
    m=trimesh.load(dest,force='mesh')
    item={'path':rel,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'matches_workspace_upstream':True,'bounds_mm':m.bounds.tolist(),'size_mm':m.extents.tolist(),'triangles':len(m.faces),'watertight':bool(m.is_watertight),'geometry_status':'UNMODIFIED ORIGINAL — not MG996R converted'}
    print('Verified exact original:',rel,flush=True)
    return item

def tf(xyz=(0,0,0),rpy=(0,0,0)):
    m=np.eye(4);m[:3,:3]=Rotation.from_euler('xyz',rpy).as_matrix();m[:3,3]=xyz;return m
def origin(el):
    o=el.find('origin')
    return tf(np.fromstring(o.get('xyz','0 0 0'),sep=' ')*1000,np.fromstring(o.get('rpy','0 0 0'),sep=' ')) if o is not None else np.eye(4)
def values(m):
    # Three.js Euler XYZ is intrinsic; URDF RPY is extrinsic.
    return {'position':m[:3,3].tolist(),'rotation':Rotation.from_matrix(m[:3,:3]).as_euler('XYZ',degrees=True).tolist()}

def main():
    paths=['Individual/'+n+'.stl' for n in NAMES]+['Follower/Ender_Follower_SO101.stl','Leader/Ender_Leader_SO101.stl']
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: source=list(ex.map(fetch,paths))
    provenance={'repository':'https://github.com/TheRobotStudio/SO-ARM100','commit':COMMIT,'files':source}
    (ROOT/'source/provenance.json').write_text(json.dumps(provenance,indent=2))
    shutil.copy2(REPO/'LICENSE',ROOT/'source/LICENSE')
    for n in NAMES:
        match=list((REPO/'STEP/SO101').rglob(n+'.step'))
        if match:shutil.copy2(match[0],ROOT/'source/STEP'/match[0].name)
    shutil.copy2(REPO/'Simulation/SO101/so101_new_calib.urdf',ROOT/'source/so101_new_calib.urdf')
    parts=[];nodes=[];instances=[];plates=[];meshes={}
    def part(n,file,kind='print',notes='Exact upstream STL. Original STS3215 interfaces; MG996R fit NOT released.'):
        m=trimesh.load(file,force='mesh');meshes[n]=m
        dest=WEB/(n+'.stl');shutil.copy2(file,dest)
        p={'id':n,'label':n.replace('_SO101','').replace('_',' '),'file':n+'.stl','kind':kind,'bounds':m.extents.tolist(),'watertight':bool(m.is_watertight),'volume_mm3':float(m.volume),'notes':notes,'quantity':{'follower':0,'leader':0}}
        parts.append(p)
    for n in NAMES:part(n,ROOT/'source/Individual'/(n+'.stl'))
    for n in ['sts3215_03a_v1','sts3215_03a_no_horn_v1']:
        m=trimesh.load(REPO/'Simulation/SO101/assets'/(n+'.stl'));m.apply_scale(1000);p=ROOT/'output'/(n+'.stl');m.export(p)
        part(n,p,'hardware','Original STS3215 reference mesh from the upstream simulation; NOT an MG996R.')
    byid={p['id']:p for p in parts}
    def node(n,parent=None,m=None,joint=None):nodes.append({'id':n,'parent':parent,**values(np.eye(4) if m is None else m),'joint':joint})
    def inst(n,parent,m,robot):
        instances.append({'id':robot+'_'+n+'_'+str(len(instances)),'part':n,'node':parent,'robot':robot,**values(m)})
        byid[n]['quantity'][robot]+=1
    mapping={
      'base_motor_holder_so101_v1':'Base_motor_holder_SO101','base_so101_v2':'Base_SO101',
      'motor_holder_so101_base_v1':'Motor_holder_SO101_Base','motor_holder_so101_wrist_v1':'Motor_holder_SO101_Wrist',
      'under_arm_so101_v1':'Under_arm_SO101','upper_arm_so101_v1':'Upper_arm_SO101',
      'rotation_pitch_so101_v1':'Rotation_Pitch_SO101','wrist_roll_pitch_so101_v2':'Wrist_Roll_Pitch_SO101',
      'waveshare_mounting_plate_so101_v2':'WaveShare_Mounting_Plate_SO101',
      'wrist_roll_follower_so101_v1':'Wrist_Roll_Follower_SO101','moving_jaw_so101_v1':'Moving_Jaw_SO101'}
    urdf=ET.parse(ROOT/'source/so101_new_calib.urdf').getroot()
    order=['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper','gripper_frame_joint']
    joints=sorted(urdf.findall('joint'),key=lambda j:order.index(j.get('name')))
    limits=[]
    for j in joints:
        lim=j.find('limit')
        if j.get('type')!='fixed':limits.append([round(np.degrees(float(lim.get(k))),1) for k in ['lower','upper']])
    preview=json.loads((ROOT/'preview-config.json').read_text())
    spacing=preview['display_base_spacing_mm']
    for robot,x in [('follower',-spacing/2),('leader',spacing/2)]:
        node(robot,m=tf([x,0,2.4]));node(robot+'_base_link',robot)
        index=0
        for j in joints:
            child=j.find('child').get('link');parent=j.find('parent').get('link');fixed=robot+'_'+child+'_datum'
            node(fixed,robot+'_'+parent,origin(j));node(robot+'_'+child,fixed,joint=index if j.get('type')!='fixed' else None)
            if j.get('type')!='fixed':index+=1
        for link in urdf.findall('link'):
            ln=link.get('name');par=robot+'_'+ln
            for v in link.findall('visual'):
                filename=Path(v.find('geometry/mesh').get('filename')).stem;n=mapping.get(filename,filename);m=origin(v)
                if robot=='leader' and n=='Wrist_Roll_Follower_SO101':
                    # Common roll housing shares the original axis and silhouette.
                    inst('Wrist_Roll_SO101',par,m@tf([0,-.218214,.949706]),robot)
                    # Leader handle datum inferred from mounting planes, not upstream leader URDF.
                    inst('Handle_SO101',par,m@tf([0,-.218214,.949706]),robot)
                elif robot=='leader' and n=='Moving_Jaw_SO101':inst('Trigger_SO101',par,m,robot)
                else:inst(n,par,m,robot)
    for robot in ['follower','leader']:
        n='Ender_'+robot.title()+'_SO101';path=ROOT/'source'/robot.title()/(n+'.stl')
        m=trimesh.load(path,force='mesh');meshes[n]=m;shutil.copy2(path,WEB/(n+'.stl'))
        # Keep original mesh bytes/orientation; a rigid placement centres the plate.
        offset=np.array([(256-m.extents[0])/2,30+(226-m.extents[1])/2,0])-m.bounds[0]
        mat=tf(offset);bounds=m.bounds+offset
        assert np.all(bounds[0]>=-1e-3) and np.all(bounds[1]<=[256,256,256])
        parts.append({'id':n,'label':'Original '+robot+' print layout','file':n+'.stl','kind':'plate','bounds':m.extents.tolist(),'watertight':bool(m.is_watertight),'notes':'Untouched Ender layout, placed on P1S. Original parts, NOT an MG996R conversion.'})
        scene=trimesh.Scene(m.copy());scene.apply_transform(mat);scene.export(str(WEB/(n+'_P1S.3mf')))
        plates.append({'id':n,'label':'Original SO-101 '+robot,'robot':robot,'count':len(m.split(only_watertight=False)),'height':round(m.extents[2],2),'entries':[{'part':n,'matrix':mat.T.reshape(-1).tolist()}],'file':n+'_P1S.3mf','placed_bounds_mm':bounds.tolist()})
    pending=nodes[:];nodes=[];seen=set()
    while pending:
        ready=[n for n in pending if n['parent'] is None or n['parent'] in seen]
        assert ready,'Unresolved joint parents'
        for n in ready:nodes.append(n);seen.add(n['id']);pending.remove(n)
    manifest={'revision':'SO101-source','status':'Original geometry imported. MG996R adaptation NOT complete. Leader trigger pose provisional.','source':provenance,'parts':parts,'nodes':nodes,'instances':instances,'plates':plates,'jointNames':['Base rotation','Shoulder','Elbow','Wrist pitch','Wrist roll','Gripper / trigger'],'home':[0,-25,35,0,0,20],'limits':limits,'parameters':{},'leader_pose_verified':False}
    manifest['display_base_spacing_mm']=spacing
    (ROOT/'output/manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(ROOT/'output/manifest.json',WEB/'manifest.json')
    shutil.copy2(ROOT/'source/provenance.json',WEB/'provenance.json')
    with zipfile.ZipFile(WEB/'SO101-originals.zip','w',zipfile.ZIP_DEFLATED) as z:
        if (ROOT/'README.md').exists():z.write(ROOT/'README.md','READ-ME-FIRST.md')
        for p in (ROOT/'source').rglob('*'):
            if p.is_file():z.write(p,p.relative_to(ROOT))
    print('Original source package and viewer manifest ready.',flush=True)

if __name__=='__main__':main()
