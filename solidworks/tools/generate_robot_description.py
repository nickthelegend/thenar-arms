"""Portable kinematic description from measured CAD; unknown dynamics stay absent."""
from pathlib import Path
import json,math,shutil,numpy as np,trimesh,yaml,xml.etree.ElementTree as ET
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2];PKG=ROOT/'ros2_ws/src/so101_description';rig=json.loads((ROOT/'simulation/cad_rig.json').read_text())
for name in ['urdf','meshes/visual','meshes/collision','config','launch','rviz']:(PKG/name).mkdir(parents=True,exist_ok=True)
partmap={'MG996R_body_R3':'MG996R_Nominal_R3','metal_horn_R3':'Metal_Horn_D20_PCD14_R3'}
def nums(v):return ' '.join(f'{float(x):.15g}' for x in v)
def transform_origin(parent,t):
    t=np.array(t);ET.SubElement(parent,'origin',xyz=nums(t[:3,3]*.001),rpy=nums(Rotation.from_matrix(t[:3,:3]).as_euler('xyz')))
def mesh_element(parent,path):ET.SubElement(ET.SubElement(parent,'geometry'),'mesh',filename='package://so101_description/'+path)
for path in (ROOT/'solidworks/exports/visual_mm').glob('*.stl'):
    mesh=trimesh.load(path);mesh.apply_scale(.001);mesh.export(PKG/'meshes/visual'/path.name)
prep=json.loads((ROOT/'verification/cad_collision_mesh_preparation.json').read_text());collision={}
for r in prep:
    m=trimesh.load(r['path']);m.apply_scale(.001);name=Path(r['path']).name;m.export(PKG/'meshes/collision'/name)
    collision.setdefault(r['part'],[]).append(name)
robot=ET.Element('robot',name='so101_mg996r_follower_r3')
robot.append(ET.Comment(' Engineering prototype. Kinematics checked against SolidWorks. Physical mass, COM, inertia and effort remain UNVERIFIED. No inertial guesses. Effort zero deliberately disables effort authority; it is not a measured servo rating. '))
colors={'printed':'.8 .25 .07 1','servo':'.12 .14 .17 1','horn':'.72 .56 .25 1'}
for name,rgba in colors.items():ET.SubElement(ET.SubElement(robot,'material',name=name),'color',rgba=rgba)
visual_records=[]
for link in rig['links']:
    le=ET.SubElement(robot,'link',name=link['name'])
    for c in link['components']:
        part=partmap.get(c['source_part'],c['source_part']);ve=ET.SubElement(le,'visual',name=c['id'])
        transform_origin(ve,c['local_transform_mm']);mesh_element(ve,'meshes/visual/'+part+'.stl')
        material='servo' if part=='MG996R_Nominal_R3' else 'horn' if part=='Metal_Horn_D20_PCD14_R3' else 'printed'
        ET.SubElement(ve,'material',name=material)
        if part=='MG996R_Nominal_R3':
            primitives=[('case',[2.05,0,-10],'box',[40.9,20,37]),('tabs',[2.05,0,-.4],'box',[54,20,2.6]),('boss',[12.5,0,10],'cylinder',[6.5,3]),('shaft',[12.5,0,11.35],'cylinder',[3,5.7])]
            for label,center,kind,size in primitives:
                ce=ET.SubElement(le,'collision',name=c['id']+'_'+label);t=np.eye(4);t[:3,3]=center;transform_origin(ce,np.array(c['local_transform_mm'])@t);ge=ET.SubElement(ce,'geometry')
                if kind=='box':ET.SubElement(ge,'box',size=nums(np.array(size)*.001))
                else:ET.SubElement(ge,'cylinder',radius=str(size[0]*.001),length=str(size[1]*.001))
        else:
            for k,name in enumerate(collision[part]):
                ce=ET.SubElement(le,'collision',name=c['id']+f'_body{k}');transform_origin(ce,c['local_transform_mm']);mesh_element(ce,'meshes/collision/'+name)
        visual_records.append({'id':c['id'],'link':link['name'],'part':part,'local_transform_mm':c['local_transform_mm']})
for j in rig['joints']:
    je=ET.SubElement(robot,'joint',name=j['joint_name'],type='revolute');ET.SubElement(je,'parent',link=j['parent_link']);ET.SubElement(je,'child',link=j['child_link'])
    ET.SubElement(je,'origin',xyz=nums(j['origin_xyz_m']),rpy=nums(j['origin_rpy_rad']));ET.SubElement(je,'axis',xyz='0 0 1')
    ET.SubElement(je,'limit',lower=str(math.radians(j['minimum_degrees'])),upper=str(math.radians(j['maximum_degrees'])),effort='0',velocity=str(j['velocity_limit_rad_s']))
tool=rig['tool_frame'];ET.SubElement(robot,'link',name=tool['name']);je=ET.SubElement(robot,'joint',name='gripper_tool_fixed',type='fixed');ET.SubElement(je,'parent',link=tool['parent']);ET.SubElement(je,'child',link=tool['name']);transform_origin(je,tool['local_transform_mm'])
ET.indent(robot,space='  ');urdf=ET.tostring(robot,encoding='unicode');(PKG/'urdf/so101.urdf').write_text('<?xml version="1.0"?>\n'+urdf+'\n')
(PKG/'urdf/so101.urdf.xacro').write_text('<?xml version="1.0"?>\n'+urdf.replace('<robot name=', '<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name=',1)+'\n')
(PKG/'package.xml').write_text('''<?xml version="1.0"?>
<package format="3"><name>so101_description</name><version>0.1.0</version><description>CAD-derived SO101 MG996R R3 engineering-prototype kinematics; dynamics unverified.</description><maintainer email="unassigned@example.invalid">Project maintainers</maintainer><license>LicenseRef-Original-Project-Source-Terms</license><buildtool_depend>ament_cmake</buildtool_depend><exec_depend>robot_state_publisher</exec_depend><exec_depend>joint_state_publisher_gui</exec_depend><exec_depend>rviz2</exec_depend><exec_depend>xacro</exec_depend><exec_depend>launch</exec_depend><exec_depend>launch_ros</exec_depend><exec_depend>ament_index_python</exec_depend><export><build_type>ament_cmake</build_type></export></package>
''')
(PKG/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.8)
project(so101_description)
find_package(ament_cmake REQUIRED)
install(DIRECTORY urdf meshes config launch rviz DESTINATION share/${PROJECT_NAME})
ament_package()
''')
(PKG/'config/joint_limits.yaml').write_text(yaml.safe_dump({'status':'Source software limits, not physical travel certification; table collisions documented','joint_limits':{j['joint_name']:{'has_position_limits':True,'min_position':math.radians(j['minimum_degrees']),'max_position':math.radians(j['maximum_degrees']),'has_velocity_limits':True,'max_velocity':j['velocity_limit_rad_s'],'has_effort_limits':False,'max_effort':None} for j in rig['joints']}},sort_keys=False))
(PKG/'config/ros2_control_mapping.yaml').write_text(yaml.safe_dump({'status':'Mapping only; no hardware plugin or control deployment provided','joints':{j['joint_name']:{'pca9685_channel':j['servo_channel'],'command_interface':'position','feedback':'UNAVAILABLE from ordinary MG996R three-wire interface','sign_default':j['servo_sign'],'zero_us':j['servo_zero_us'],'us_per_degree':j['us_per_degree'],'mechanical_reduction':1,'physical_calibration':'UNVERIFIED'} for j in rig['joints']}},sort_keys=False))
(PKG/'launch/display.launch.py').write_text('''from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    share = Path(get_package_share_directory('so101_description'))
    description = xacro.process_file(str(share / 'urdf/so101.urdf.xacro')).toxml()
    return LaunchDescription([
        Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[{'robot_description': description}]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2', arguments=['-d', str(share / 'rviz/so101.rviz')]),
    ])
''')
(PKG/'rviz/so101.rviz').write_text('''Panels:
  - Class: rviz_common/Displays
Visualization Manager:
  Global Options:
    Fixed Frame: base_link
  Displays:
    - Class: rviz_default_plugins/RobotModel
      Name: Robot
      Enabled: true
      Description Source: Topic
      Description Topic:
        Value: /robot_description
    - Class: rviz_default_plugins/Grid
      Name: Grid
      Enabled: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 0.65
      Pitch: 0.45
      Yaw: 0.7
''')
(PKG/'README.md').write_text('''# SO101 MG996R R3 description

Engineering prototype, not physically tested or payload rated. Generated from the checked SolidWorks reconstruction and measured component transforms.

Run `colcon build --packages-select so101_description`, source the install setup, then `ros2 launch so101_description display.launch.py` on a ROS 2 installation. ROS 2 GUI/build validation is not available in this Windows task environment; standalone Xacro/XML/kinematic validation is separate.

Six revolute joints include the directly driven moving jaw. The base frame retains the source convention. Add a +0.0024 m world-Z placement to match the SolidWorks tabletop scene. Mesh coordinates and URDF origins are metres.

No physical inertial guesses are included. Effort=0 deliberately grants no effort authority; it is not a servo rating. Velocity=10 deg/s is the existing firmware command slew ceiling. This geometry package does not provide a hardware driver, measured feedback, payload rating or physical-dynamics validation.

The servo collision envelope uses its exact source boxes and cylinders. Other collision meshes preserve the CAD solids. No convex print proxy has been accepted; do not let a physics importer silently replace each concave link with one convex hull. Shaft/horn spline engagement is intentional in the source. J2 and J3 maximum-at-other-joints-zero poses penetrate the tabletop.

Original project asset licensing still applies; no new license rights are asserted by this generated package.
''')
(ROOT/'simulation/urdf_visual_mapping.json').write_text(json.dumps(visual_records,indent=2))
print('Generated',PKG,'links',len(robot.findall('link')),'joints',len(robot.findall('joint')))
