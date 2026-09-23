"""Inspect MuJoCo's importer behavior without accepting its inferred dynamics."""
from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET,mujoco,numpy as np
ROOT=Path(__file__).resolve().parents[2];pkg=ROOT/'ros2_ws/src/so101_description';out=ROOT/'simulation/mujoco';(out/'meshes').mkdir(parents=True,exist_ok=True)
robot=ET.parse(pkg/'urdf/so101.urdf').getroot()
for mesh in robot.findall('.//mesh'):
    source=pkg/mesh.attrib['filename'].removeprefix('package://so101_description/');dest=out/'meshes'/source.name;shutil.copy2(source,dest);mesh.attrib['filename']=source.name
compiler=ET.SubElement(ET.SubElement(robot,'mujoco'),'compiler',meshdir='meshes',discardvisual='false',fusestatic='false')
ET.indent(robot,space='  ');path=out/'so101_import_test.urdf';ET.ElementTree(robot).write(path,encoding='utf-8',xml_declaration=True)
report={'mujoco_version':mujoco.__version__,'source_urdf':str(path),'actual_physical_mass_COM_inertia':'UNVERIFIED; no importer-generated values will be accepted as physical robot data'}
try:
    model=mujoco.MjModel.from_xml_path(str(path));data=mujoco.MjData(model)
    report.update(import_result='LOADED for kinematic inspection only',njnt=model.njnt,nbody=model.nbody,ngeom=model.ngeom,engine_body_mass_kg=model.body_mass.tolist(),physical_model_status='REJECTED for dynamics: importer inferred mass/inertia from collision geometry')
    poses=json.loads((ROOT/'verification/urdf_validation.json').read_text())['pose_regressions'];rig=json.loads((ROOT/'simulation/cad_rig.json').read_text());results=[]
    for pose in poses:
        for j,q in zip(rig['joints'],np.deg2rad(pose['joint_degrees'])):
            id=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,j['joint_name']);assert id>=0,j['joint_name'];data.qpos[model.jnt_qposadr[id]]=q
        mujoco.mj_forward(model,data);errors=[]
        for name,t in pose['link_transforms_robot_base_m'].items():
            id=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,name)
            if id<0:
                if name=='base_link':continue
                raise AssertionError(('Missing body',name))
            t=np.array(t);errors.append(float(np.linalg.norm(data.xpos[id]-t[:3,3])));errors.append(float(np.max(abs(data.xmat[id].reshape(3,3)-t[:3,:3]))))
        results.append({'pose':pose['pose'],'max_position_or_rotation_matrix_error':max(errors),'pass':max(errors)<1e-7})
    report['kinematic_regression']=results;report['kinematic_pass']=all(r['pass'] for r in results)
    # No stepping: inferred dynamics are explicitly unaccepted.
    report['dynamic_sanity_test']='NOT RUN: required physical inertias are unknown'
except Exception as e:report.update(import_result='FAILED',error=str(e),kinematic_pass=False)
(ROOT/'verification/mujoco_urdf_import.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='kinematic_regression'},indent=2),flush=True)
