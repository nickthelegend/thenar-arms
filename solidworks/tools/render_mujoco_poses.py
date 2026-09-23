"""Visual inspection only: forward kinematics, no dynamics steps/inertia acceptance."""
from pathlib import Path
import json,numpy as np,mujoco
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'verification/pose_images';out.mkdir(exist_ok=True)
model=mujoco.MjModel.from_xml_path(str(ROOT/'simulation/mujoco/so101_import_test.urdf'));data=mujoco.MjData(model)
model.vis.global_.offwidth=1200;model.vis.global_.offheight=1000
model.vis.headlight.ambient[:]=[.55,.55,.55];model.vis.headlight.diffuse[:]=[.9,.9,.9]
rig=json.loads((ROOT/'simulation/cad_rig.json').read_text());poses={'ZERO':[0]*6,'J1_MAX':[85,0,0,0,0,0],'J2_MIN':[0,-80,0,0,0,0],'MULTI':[20,-30,40,-20,30,25],'HOME':[0,-25,35,0,0,20]}
camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera);camera.lookat[:]=[.13,0,.12];camera.distance=.75;camera.azimuth=135;camera.elevation=-29.5
camera_records={}
options=mujoco.MjvOption();mujoco.mjv_defaultOption(options);options.geomgroup[:]=0;options.geomgroup[1]=1
print('Geom groups:',dict(zip(*np.unique(model.geom_group,return_counts=True))),flush=True)
assert np.count_nonzero(model.geom_group==1)==19,'Expected 19 visual instances'
with mujoco.Renderer(model,height=1000,width=1200) as renderer:
    for name,q in poses.items():
        for joint,value in zip(rig['joints'],np.deg2rad(q)):
            i=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,joint['joint_name']);data.qpos[model.jnt_qposadr[i]]=value
        mujoco.mj_forward(model,data)
        points=[]
        for g in np.flatnonzero(model.geom_group==1):
            mid=model.geom_dataid[g];start=model.mesh_vertadr[mid];count=model.mesh_vertnum[mid];verts=model.mesh_vert[start:start+count]
            points.append(verts@data.geom_xmat[g].reshape(3,3).T+data.geom_xpos[g])
        points=np.vstack(points);lo=points.min(0);hi=points.max(0);camera.lookat[:]=(lo+hi)/2
        radius=np.max(np.linalg.norm(points-camera.lookat,axis=1));camera.distance=float(radius/np.sin(np.radians(model.vis.global_.fovy/2))*1.2)
        camera_records[name]={'lookat_m':camera.lookat.tolist(),'distance_m':camera.distance,'radius_m':float(radius),'fit_margin':1.2}
        renderer.update_scene(data,camera=camera,scene_option=options);Image.fromarray(renderer.render()).save(out/f'mujoco_{name}.png');print('Rendered',name,flush=True)
(out/'mujoco_render_scope.json').write_text(json.dumps({'method':'MuJoCo 3.14.0 URDF import, visual group 1 only, mj_forward only; inferred masses remain REJECTED, no dynamics stepping','poses':poses,'camera':{'azimuth_degrees':camera.azimuth,'elevation_degrees':camera.elevation,'per_pose_fits':camera_records}},indent=2))
