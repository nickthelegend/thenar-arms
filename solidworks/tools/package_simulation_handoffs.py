"""Preserve unknown physics explicitly; package structural simulator handoffs."""
from pathlib import Path
import json, shutil, xml.etree.ElementTree as ET
import numpy as np, yaml
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2]
rig=json.loads((ROOT/'simulation/cad_rig.json').read_text())
props=yaml.safe_load((ROOT/'simulation/inertial_properties.yaml').read_text())
parts={p['part']:p for p in props['part_geometry']}
aliases={'MG996R_body_R3':'MG996R_Nominal_R3','metal_horn_R3':'Metal_Horn_D20_PCD14_R3'}
links=[]
for link in rig['links']:
    terms=[]
    for c in link['components']:
        part=aliases.get(c['source_part'],c['source_part']);t=np.array(c['local_transform_mm']);r=t[:3,:3]
        for k,b in enumerate(parts[part]['bodies']):
            mp=b['raw_mass_properties_SI_density_1'];com=r@np.array(mp[:3])+t[:3,3]*.001
            inertia=np.array([[mp[6],-mp[9],-mp[10]],[-mp[9],mp[7],-mp[11]],[-mp[10],-mp[11],mp[8]]]);inertia=r@inertia@r.T
            terms.append({'component':c['id'],'part':part,'body':k,'volume_m3':mp[3], 'uniform_geometry_centroid_in_link_m':com.tolist(),'central_inertia_per_density_m5':inertia.tolist(),'physical_density_kg_m3':None})
    links.append({'link':link['name'],'mass_kg':None,'center_of_mass_m':None,'inertia_kg_m2':None,'inertial_frame':link['name'],'status':'UNVERIFIED physical properties; geometric coefficients below are not physical assignments','geometric_terms':terms})
props['rigid_links']=links
(ROOT/'simulation/inertial_properties.yaml').write_text(yaml.safe_dump(props,sort_keys=False))
pkg=ROOT/'ros2_ws/src/so101_description'
for path in [pkg/'package.xml',ROOT/'solidworks/tools/generate_robot_description.py']:
    text=path.read_text();text=text.replace('<exec_depend>launch_ros</exec_depend>','<exec_depend>launch_ros</exec_depend><exec_depend>ament_index_python</exec_depend>') if 'exec_depend>ament_index_python' not in text else text;path.write_text(text)
out=ROOT/'simulation/mujoco';out.mkdir(exist_ok=True)
root=ET.Element('mujoco',model='so101_structural_template_PHYSICS_BLOCKED')
root.append(ET.Comment(' PHYSICS BLOCKED: insert measured link inertials before loading. inertiafromgeom=false deliberately prevents silent invented masses. See README.md and ../inertial_properties.yaml. '))
ET.SubElement(root,'compiler',angle='radian',meshdir='meshes',inertiafromgeom='false')
asset=ET.SubElement(root,'asset');wb=ET.SubElement(root,'worldbody');bodies={};seen=set()
def numbers(xs):return ' '.join(f'{x:.15g}' for x in xs)
for link in rig['links']:
    j=next((j for j in rig['joints'] if j['child_link']==link['name']),None)
    attrs={'name':link['name']}
    if j:
        attrs.update(pos=numbers(j['origin_xyz_m']),quat=numbers(Rotation.from_euler('xyz',j['origin_rpy_rad']).as_quat(scalar_first=True)))
    body=ET.SubElement(bodies[j['parent_link']] if j else wb,'body',**attrs);bodies[link['name']]=body
    if j:ET.SubElement(body,'joint',name=j['joint_name'],type='hinge',axis='0 0 1',limited='true',range=numbers(np.deg2rad([j['minimum_degrees'],j['maximum_degrees']])))
    body.append(ET.Comment(' Physical inertial element intentionally absent: UNVERIFIED. '))
    for c in link['components']:
        part=aliases.get(c['source_part'],c['source_part']);t=np.array(c['local_transform_mm'])
        if part not in seen:ET.SubElement(asset,'mesh',name=part,file=part+'.stl');seen.add(part)
        ET.SubElement(body,'geom',name=c['id'],type='mesh',mesh=part,pos=numbers(t[:3,3]*.001),quat=numbers(Rotation.from_matrix(t[:3,:3]).as_quat(scalar_first=True)),contype='0',conaffinity='0',group='2')
ET.indent(root,space='  ');ET.ElementTree(root).write(out/'so101.xml',encoding='utf-8',xml_declaration=True)
(out/'README.md').write_text('''# MuJoCo handoff: kinematics checked, physical simulation blocked

`so101_import_test.urdf` was loaded in MuJoCo 3.14.0 and all 28 canonical link-pose comparisons passed. The importer silently inferred masses; these were rejected as physical robot properties. No dynamics steps were accepted or reported as physical verification.

`so101.xml` preserves the six-joint structural tree and visuals. It deliberately sets `inertiafromgeom="false"` and contains no fabricated inertials. MuJoCo must reject loading it until measured/supported link mass, COM and inertia are entered. Visual geoms have contacts disabled; validated convex contact proxies remain outstanding. This file is a structural template, not a runnable physical model.

The exact CAD collision meshes and raw intentional shaft/horn overlaps are retained in the ROS package. A 0.1 mm convex decomposition trial became impractically fragmented and was abandoned without accepting geometry. Do not replace each concave print with one convex hull. Damping, friction, armature, contact properties and actuator dynamics are unknown; future values must be separately labelled tuning assumptions.

Run `../../solidworks/tools/test_mujoco_urdf_import.py` from the project Python environment for the reproducible forward-kinematic inspection. Evidence: `../../verification/mujoco_urdf_import.json`.
''')
import mujoco
try:
    mujoco.MjModel.from_xml_path(str(out/'so101.xml'));guard={'expected_rejection':False,'error':'Unexpected load success'}
except ValueError as e:guard={'expected_rejection':'mass and inertia' in str(e),'error':str(e)}
assert guard['expected_rejection'],guard
(ROOT/'verification/mujoco_physics_guard.json').write_text(json.dumps(guard,indent=2))
isaac=ROOT/'simulation/isaac'
for p in ['source_urdf','usd','config','validation']:(isaac/p).mkdir(parents=True,exist_ok=True)
robot=ET.parse(pkg/'urdf/so101.urdf')
for mesh in robot.findall('.//mesh'):
    relative=mesh.attrib['filename'].removeprefix('package://so101_description/');dst=isaac/'source_urdf'/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pkg/relative,dst);mesh.attrib['filename']=relative
robot.write(isaac/'source_urdf/so101.urdf',encoding='utf-8',xml_declaration=True)
shutil.copy2(ROOT/'verification/urdf_validation.json',isaac/'validation/canonical_pose_reference.json')
(isaac/'config/import_requirements.yaml').write_text(yaml.safe_dump({'status':'NOT RUN: Isaac Sim not available in this task environment','distance_unit':'metre','fix_base':True,'merge_fixed_joints':False,'physical_inertials':'BLOCKED; do not accept importer defaults','joint_drive':'No measured actuator model; no default gains accepted','collision':'Preserve exact reference meshes; validated convex decomposition required for dynamic links','validation_reference':'../validation/canonical_pose_reference.json','root_world_z_for_CAD_scene_m':.0024},sort_keys=False))
(isaac/'README.md').write_text('''# Isaac Sim import handoff

Import `source_urdf/so101.urdf` using the URDF importer in the installed Isaac Sim release. Relative mesh paths are self-contained. Follow `config/import_requirements.yaml`; compare the same joint vectors to `validation/canonical_pose_reference.json` in metres before accepting articulation.

Isaac Sim was unavailable in this task environment, so no import, USD or dynamics validation is claimed. `usd/` is intentionally empty. Missing physical inertials and unaccepted convex collision proxies block trustworthy physics. Do not accept automatic density, mass, drive gains or single-convex-hull approximations as measured robot data. Preserve the original dimensions and source joint limits.
''')
print('Prepared 7 per-link unknown-inertia records, guarded MJCF, and self-contained Isaac URDF assets; guard verified.')
