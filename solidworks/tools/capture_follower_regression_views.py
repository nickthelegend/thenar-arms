"""Native CAD images from an isolated copy, with numerical pose checks per capture."""
from check_assembly_pose import *
from probe_joint_motion import posed_worlds
from real_limit_mates import set_pose
from PIL import Image
import shutil

def main():
    out=ROOT/'verification/pose_images';out.mkdir(exist_ok=True);s=attach();master=ROOT/'solidworks/assemblies/SO101_Follower_Master.SLDASM';copy=ROOT/'solidworks/checkpoints/Follower_visual_regression.SLDASM';shutil.copy2(master,copy)
    d,e,w=s.OpenDoc6(str(copy),2,1,'',0,0);assert d is not None,(e,w);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc');m=load_manifest();build=json.loads((ROOT/'solidworks/evidence/follower_assembly_build.json').read_text());results=[]
    doc.ShowConfiguration2('FREE_MOTION');doc.ForceRebuild3(False);feats=mate_features(doc)
    poses={'ZERO':[0]*6,'J1_MAX':[85,0,0,0,0,0],'J2_MIN':[0,-80,0,0,0,0],'MULTI':[20,-30,40,-20,30,25],'HOME':[0,-25,35,0,0,20]}
    for name,q in poses.items():
        set_pose(doc,feats,q,m['limits'],force=True);world=posed_worlds(m,q);byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']};errors=[]
        for i in m['instances']:
            a=from_sw(cs[i['id']]);b=world[i['node']]@matrix(i);errors.append((float(np.linalg.norm(a[:3,3]-b[:3,3])),float(np.degrees(Rotation.from_matrix(b[:3,:3].T@a[:3,:3]).magnitude()))))
        row={'pose':name,'q_degrees':q,'max_position_error_mm':max(e[0] for e in errors),'max_angle_error_deg':max(e[1] for e in errors),'mate_errors':[n for n,f in feats.items() if f.GetErrorCode2()[0]!=0]};assert max(row['max_position_error_mm'],row['max_angle_error_deg'])<.001 and not row['mate_errors'],row
        doc.ClearSelection2(True);doc.SetUserPreferenceToggle(CONST.swViewDisplayHideAllTypes,True);v=typed(doc.ActiveView,'IModelView');z=np.array([1.,-1.,.8]);z/=np.linalg.norm(z);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);t=np.eye(4);t[:3,:3]=[x,y,z];v.Orientation3=sw_transform(s,t);doc.ViewDisplayShaded();doc.ViewZoomtofit2();image=out/f'solidworks_{name}.bmp';assert doc.SaveBMP(str(image),1200,1000);Image.open(image).save(image.with_suffix('.png'));results.append(row);print(row,flush=True)
    (out/'solidworks_render_scope.json').write_text(json.dumps({'method':'Native SolidWorks SaveBMP from isolated master copy; all 19 transforms measured at each captured mate-driven pose. Delivered master never modified by this script.','poses':results},indent=2));s.CloseDoc(doc.GetTitle())
if __name__=='__main__':main()
