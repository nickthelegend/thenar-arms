"""Local SO101 wrist extension to separate the two nominal MG996Rs.

Not an assembly release: independent pair checks are deliberately narrower than
the complete arm collision check. Preserve original interfaces and extend only
a section between the pitch and roll motor locations, without scaling meshes.
"""
import json,hashlib,shutil
import cadquery as cq
import numpy as np
from scipy.spatial.transform import Rotation
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from clearance_study import ROOT,WEB,matrix,transform,servo,box
from build_fit_test import export_mesh

DEST=ROOT/'output/wrist-spacing-r2'

def main():
    DEST.mkdir(exist_ok=True)
    m=json.loads((WEB/'study-manifest.json').read_text());w={}
    for n in m['nodes']:w[n['id']]=(w[n['parent']] if n['parent'] else np.eye(4))@matrix(n)
    inst=m['instances']
    a=next(i for i in inst if i['id']=='follower_sts3215_03a_v1_11')
    b=next(i for i in inst if i['id']=='follower_sts3215_03a_no_horn_v1_12')
    p=next(i for i in inst if i['id']=='follower_Wrist_Roll_Pitch_SO101_13')
    aw=w[a['node']]@matrix(a);bw=w[b['node']]@matrix(b);pw=w[p['node']]@matrix(p)
    original=cq.importers.importStep(str(ROOT/'source/STEP/Wrist_Roll_Pitch_SO101.step')).val().Solids()[0]
    split=18.;extra=8.
    lower=original.intersect(box(200,200,118,(0,0,-100))).translate((0,0,-extra))
    upper=original.intersect(box(200,200,100,(0,0,split)))
    sections=[f for f in upper.Faces() if f.BoundingBox().zlen<1e-5 and abs(f.Center().z-split)<1e-5]
    assert sections,'No cross-section at extension plane'
    extension=upper.fuse(lower)
    for face in sections:
        bridge=cq.Shape.cast(BRepPrimAPI_MakePrism(face.wrapped,gp_Vec(0,0,-extra)).Shape())
        extension=extension.fuse(bridge)
    extension=extension.clean()
    assert extension.isValid() and len(extension.Solids())==1
    # Servo shift is along its shaft axis. Child gripper joint must also move
    # 8 mm away from the pitch joint; no joint is silently moved in the web app.
    shifted=np.eye(4);shifted[2,3]=extra
    roll_local=np.linalg.inv(pw)@bw@shifted
    pitch_local=np.linalg.inv(pw)@aw
    cavity=transform(servo(.3),roll_local)
    edited=extension.cut(cavity).cut(transform(servo(.3),pitch_local)).clean()
    counts=len(edited.Solids())
    report={'status':'WRIST SPACING PROTOTYPE — NOT A COMPLETE ARM OR PRINT RELEASE',
        'extension_mm':extra,'original_section_plane_z_mm':split,'original_source':'source/STEP/Wrist_Roll_Pitch_SO101.step',
        'unscaled_extension_valid':extension.isValid(),'unscaled_extension_solids':len(extension.Solids()),
        'clearance_cut_valid':edited.isValid(),'clearance_cut_solids':counts,
        'full_arm_verified':False,'physical_tested':False,
        'required_assembly_change':'Move follower roll-servo instance and gripper-link joint origin by 8 mm along roll output axis (wrist-link Y -= 8). Leader unchanged.',
        'limitations':['Original horn, idler and flange mounting interfaces are not converted by an extension alone.','Two-servo pair checks are NOT full assembly motion checks.','No unchanged collision report may certify this changed geometry.']}
    cq.exporters.export(extension,str(DEST/'Wrist_Roll_Pitch_SO101_extended_8mm.step'))
    if edited.isValid() and counts==1:
        cq.exporters.export(edited,str(DEST/'Wrist_Roll_Pitch_SO101_MG996R_spacing_PROTOTYPE.step'))
        try:
            mesh,tess=export_mesh(edited,DEST/'Wrist_Roll_Pitch_SO101_MG996R_spacing_PROTOTYPE.stl')
            report['watertight']=bool(mesh.is_watertight);report['tessellation']=tess
        except ValueError as e:report['mesh_failure']=str(e)
    samples=[]
    for q in range(-80,81,2):
        t=np.eye(4);t[:3,3]=[12.5,0,18.7]
        r=np.eye(4);r[:3,:3]=Rotation.from_euler('z',q,degrees=True).as_matrix()
        other=transform(servo(),t@r@np.linalg.inv(t)@np.linalg.inv(aw)@bw@shifted)
        v=max(0,servo().intersect(other).Volume());distance=servo().distance(other)
        samples.append({'wrist_pitch_degrees':q,'overlap_mm3':v,'distance_mm':distance})
    report['pair_check']={'samples':samples,'all_sampled_overlap_free':all(s['overlap_mm3']<.001 for s in samples),
        'minimum_sampled_distance_mm':min(s['distance_mm'] for s in samples),'continuous_sweep_certified':False}
    (DEST/'verification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='pair_check'},indent=2))
    print('PAIR CHECK',len(samples),'poses; minimum nominal gap',report['pair_check']['minimum_sampled_distance_mm'],flush=True)

if __name__=='__main__':main()
