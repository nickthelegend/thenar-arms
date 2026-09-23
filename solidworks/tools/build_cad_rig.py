"""Derive portable rigid-link frames from measured ZERO component transforms."""
from prepare_follower_parts import ROOT,load_manifest,matrix
import numpy as np,json,yaml
from scipy.spatial.transform import Rotation
m=load_manifest();measured=json.loads((ROOT/'solidworks/evidence/zero_pose_after_mating.json').read_text())
actual={r['id']:np.array(r['actual_transform_mm']) for r in measured}
links={};jointmap=yaml.safe_load((ROOT/'simulation/joint_map.yaml').read_text())
for i in m['instances']:
    if not i['part'].endswith('_MG996R_R3'):continue
    links[i['node']]={'name':i['node'].removeprefix('follower_'),'world_mm':actual[i['id']]@np.linalg.inv(matrix(i)),'components':[]}
for i in m['instances']:
    local=np.linalg.inv(links[i['node']]['world_mm'])@actual[i['id']]
    links[i['node']]['components'].append({'id':i['id'],'source_part':i['part'],'local_transform_mm':local.tolist()})
jointrows=[]
for n in m['nodes']:
    if n['joint'] is None:continue
    dat=next(x for x in m['nodes'] if x['id']==n['parent']);parent=links[dat['parent']];child=links[n['id']]
    origin=np.linalg.inv(parent['world_mm'])@child['world_mm'];r=jointmap['joints'][n['joint']].copy()
    r['origin_xyz_m']=(origin[:3,3]*.001).tolist();r['origin_rpy_rad']=Rotation.from_matrix(origin[:3,:3]).as_euler('xyz').tolist()
    r['evidence']='CAD measured ZERO component transforms + native joint datum readback; 28 mate-driven pose comparisons'
    r['velocity_limit_rad_s']=float(np.deg2rad(10));r['velocity_status']='SOURCE VERIFIED firmware command slew ceiling: 0.2 degrees per 20 ms; not physical speed capability'
    r['effort_limit_Nm']=None;r['physical_inertias']='UNVERIFIED';jointrows.append(r)
base=links['follower_base_link']['world_mm'].copy();base[:3,3]*=.001
tool=next(n for n in m['nodes'] if n['id']=='follower_gripper_frame_link_datum')
result={'status':'CAD-measured rigid layout; physical dynamics UNVERIFIED','units':'transforms explicitly millimetres, joint origins SI','cad_world_from_robot_base_m':base.tolist(),'links':[{**{k:v for k,v in l.items() if k!='world_mm'},'cad_zero_world_transform_mm':l['world_mm'].tolist()} for l in links.values()],'joints':jointrows,'tool_frame':{'name':'gripper_frame_link','parent':'gripper_link','local_transform_mm':matrix(tool).tolist(),'source_status':'SOURCE VERIFIED fixed tool datum; not a physical component'},'software_home_degrees':[0,-25,35,0,0,20]}
(ROOT/'simulation/cad_rig.json').write_text(json.dumps(result,indent=2))
jointmap.update(status='CAD MEASURED + SOURCE VERIFIED kinematics; physical calibration/dynamics UNVERIFIED',joints=jointrows,cad_world_from_robot_base_m=base.tolist())
(ROOT/'simulation/joint_map.yaml').write_text(yaml.safe_dump(jointmap,sort_keys=False))
print('CAD rig:',len(links),'rigid links',len(jointrows),'moving joints')
