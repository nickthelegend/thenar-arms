from pathlib import Path
import json,math,numpy as np,xml.etree.ElementTree as ET,xacro,trimesh
from scipy.spatial.transform import Rotation
from urdf_parser_py.urdf import URDF
ROOT=Path(__file__).resolve().parents[2];PKG=ROOT/'ros2_ws/src/so101_description'
expanded=xacro.process_file(str(PKG/'urdf/so101.urdf.xacro')).toxml();robot=ET.fromstring(expanded);parsed=URDF.from_xml_string(expanded)
links=robot.findall('link');joints=robot.findall('joint');names=[l.attrib['name'] for l in links];jnames=[j.attrib['name'] for j in joints]
assert len(names)==len(set(names)) and len(jnames)==len(set(jnames))
assert len(joints)==len(links)-1
children=[j.find('child').attrib['link'] for j in joints];roots=set(names)-set(children);assert roots=={'base_link'} and len(children)==len(set(children))
for j in joints:
    assert j.find('parent').attrib['link'] in names and j.find('child').attrib['link'] in names
    if j.attrib['type']=='revolute':
        axis=np.fromstring(j.find('axis').attrib['xyz'],sep=' ');assert np.linalg.norm(axis)==1
        limit=j.find('limit').attrib;assert float(limit['lower'])<=float(limit['upper']);assert float(limit['velocity'])>0;assert float(limit['effort'])==0
paths=[]
for me in robot.findall('.//mesh'):
    uri=me.attrib['filename'];assert uri.startswith('package://so101_description/');p=PKG/uri.removeprefix('package://so101_description/');assert p.is_file();paths.append(str(p.relative_to(PKG)))
assert not robot.findall('.//inertial'),'Do not inject unverified physical inertias'
def origin(element):
    t=np.eye(4);o=element.find('origin')
    if o is not None:
        t[:3,3]=np.fromstring(o.attrib.get('xyz','0 0 0'),sep=' ');t[:3,:3]=Rotation.from_euler('xyz',np.fromstring(o.attrib.get('rpy','0 0 0'),sep=' ')).as_matrix()
    return t
rig=json.loads((ROOT/'simulation/cad_rig.json').read_text());base=np.array(rig['cad_world_from_robot_base_m']);qnames=[j['joint_name'] for j in rig['joints']]
poses=json.loads((ROOT/'solidworks/evidence/joint_motion_measurements.json').read_text());results=[]
for pose in poses:
    assert pose['kinematic_pass'];q=dict(zip(qnames,np.deg2rad(pose['command_deg'])));world={'base_link':np.eye(4)};pending=joints.copy()
    while pending:
        before=len(pending)
        for j in pending.copy():
            p=j.find('parent').attrib['link'];c=j.find('child').attrib['link']
            if p not in world:continue
            t=origin(j)
            if j.attrib['type']=='revolute':
                rr=np.eye(4);rr[:3,:3]=Rotation.from_rotvec(np.fromstring(j.find('axis').attrib['xyz'],sep=' ')*q[j.attrib['name']]).as_matrix();t=t@rr
            world[c]=world[p]@t;pending.remove(j)
        assert len(pending)<before,'Disconnected or cyclic tree'
    actual={r['id']:np.array(r['measured_transform_mm']) for r in pose['components']};checks=[]
    for l in links:
        for visual in l.findall('visual'):
            id=visual.attrib['name'];t=base@world[l.attrib['name']]@origin(visual);cad=actual[id];cad[:3,3]*=.001
            checks.append({'id':id,'position_error_m':float(np.linalg.norm(t[:3,3]-cad[:3,3])),'angle_error_rad':float(Rotation.from_matrix(t[:3,:3].T@cad[:3,:3]).magnitude())})
    row={'pose':pose['name'],'joint_degrees':pose['command_deg'],'max_position_error_m':max(r['position_error_m'] for r in checks),'max_angle_error_rad':max(r['angle_error_rad'] for r in checks),'component_count':len(checks),'link_transforms_robot_base_m':{k:v.tolist() for k,v in world.items()}}
    row['pass']=row['max_position_error_m']<1e-7 and row['max_angle_error_rad']<1e-7;results.append(row)
report={'xacro_parse':'PASS','urdf_parser':'PASS','tree':'PASS','links':len(links),'joints':len(joints),'moving_joints':len(qnames),'unique_mesh_files':sorted(set(paths)),'dynamics':'UNVERIFIED; inertials omitted and effort authority set to zero','ROS2_build_and_RViz':'NOT RUN; ROS 2 unavailable in task PATH','pose_regressions':results,'pass':all(r['pass'] for r in results)}
(ROOT/'verification/urdf_validation.json').write_text(json.dumps(report,indent=2));(PKG/'urdf/so101.expanded.urdf').write_text(expanded)
print({k:v for k,v in report.items() if k not in ['unique_mesh_files','pose_regressions']});print('Maximum pose error m/rad',max(r['max_position_error_m'] for r in results),max(r['max_angle_error_rad'] for r in results));assert report['pass']
