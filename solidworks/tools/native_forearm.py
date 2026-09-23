"""Reconstruct the R3 joined forearm from its retained source pieces and native cuts."""
from sw_api import *
from native_hardware import typed,sketch
from build_follower_assembly import sw_transform
import numpy as np,json
ROOT=Path(__file__).resolve().parents[2]
def cut(doc,name,z0,z1,rect=None,circles=()):
    sketch(doc,name+'_Profile',rect,circles)
    f=typed(doc.FeatureManager,'IFeatureManager').FeatureCut4(True,False,True,0,0,(z1-z0)/1000,0,False,False,False,False,0,0,False,False,False,False,False,True,True,False,False,False,3,abs(z0)/1000,z0<0,False)
    if f is not None:typed(f,'IFeature').Name=name
    else:
        # A zero-intersection cut is not automatically an error; retain evidence and inspect.
        print('CUT FAILED',name,flush=True)
    return f
def main():
    s=attach();s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlModelType,2);s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlUnits,CONST.swMM);s.SetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh,False)
    bodycopies=[]
    for name in ['Under_arm_SO101','Motor_holder_SO101_Wrist']:
        checkpoint=ROOT/'solidworks/checkpoints'/(name+'_R3_healed.SLDPRT')
        if checkpoint.exists():d,e,wa=s.OpenDoc6(str(checkpoint),1,1,'',0,0)
        else:
            path=ROOT/'so101-mg996r/output/follower-r3/parts'/(name+'_MG996R_R3.stl')
            print('Import source',name,flush=True);d,e=s.LoadFile4(str(path),'r',None,0)
        doc=model(d);p=typed(doc,'IPartDoc');bs=p.GetBodies2(0,False);print(name,'solids',len(bs or []),flush=True)
        assert len(bs or [])==1,name
        body=typed(bs[0],'IBody2');assert body.GetMassProperties(1)[3]>0
        if not checkpoint.exists():assert doc.SaveAs3(str(checkpoint),0,1)==0
        copy=typed(body.Copy(),'IBody2')
        if name=='Motor_holder_SO101_Wrist':
            t=np.eye(4);t[:3,3]=[0,-.05,.2];assert copy.ApplyTransform(sw_transform(s,t))
        bodycopies.append(copy)
    doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0));p=typed(doc,'IPartDoc')
    for name,b in zip(['R3_Under_arm_source','R3_Wrist_holder_source_seam_offset_0p05'],bodycopies):
        f=p.CreateFeatureFromBody3(b,False,0);assert f is not None;typed(f,'IFeature').Name=name
    fm=typed(doc.FeatureManager,'IFeatureManager')
    bs=p.GetBodies2(0,False)
    # swBodyOperationType_e uses SWBODYADD=15903.
    f=fm.InsertCombineFeature(CONST.SWBODYADD,None,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,list(bs)))
    assert f is not None,'Combine failed';typed(f,'IFeature').Name='Join_source_brackets_R3_seam_overlap'
    print('Joined volume',sum(typed(b,'IBody2').GetMassProperties(1)[3]*1e9 for b in p.GetBodies2(0,False)),flush=True)
    path=ROOT/'solidworks/checkpoints/Forearm_native_join_v4.SLDPRT';assert doc.SaveAs3(str(path),0,1)==0
    # Source motor coordinates map to x=-57.5501-x, y=-37.2-y, z=-0.5+z.
    def rect(size,centre):
        x,y=-57.5501-centre[0],-37.2-centre[1];a,b=size
        return (x-a/2,y-b/2,x+a/2,y+b/2)
    def circles(rs):return [(-57.5501-x,-37.2-y,r) for x,y,r in rs]
    cut(doc,'Case_clearance_R3_41p5_x_20p6',-29.3,8.3,rect((41.5,20.6),(2.05,0)))
    cut(doc,'Tab_clearance_R3_retaining_seat',-2.2,.7,rect((54.6,20.6),(2.05,0)))
    cut(doc,'Output_boss_clearance_R3',7.7,11.3,circles=circles([(12.5,0,6.8)]))
    cut(doc,'Output_shaft_clearance_R3',7.7,14,circles=circles([(12.5,0,3.3)]))
    cut(doc,'Four_nut_access_bores_D6p8',-80.5,-6.2,circles=circles([(x,y,3.4) for x in [-22.7,26.8] for y in [-5,5]]))
    for x in [-22.7,26.8]:
        for y in [-5,5]:cut(doc,f'Slot_web_{x}_{y}',-8.5,1.5,rect((1.6,3.4),(x,y)))
    for side in [-.8,.8]:cut(doc,f'Slot_ends_{side}',-8.5,1.5,circles=circles([(x+side,y,1.7) for x in [-22.7,26.8] for y in [-5,5]]))
    doc.ForceRebuild3(False)
    doc.MaterialPropertyValues=[.8,.25,.07,1,.5,.25,.1,0,0];doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2()
    path=ROOT/'solidworks/checkpoints/Forearm_native_candidate_v4.SLDPRT';error=doc.SaveAs3(str(path),0,1)
    bs=p.GetBodies2(0,False);row={'path':str(path),'save_error':error,'body_count':len(bs or []),'volume_mm3':sum(typed(b,'IBody2').GetMassProperties(1)[3]*1e9 for b in bs or []),'acceptance':'PENDING numerical comparison; not yet accepted master geometry'}
    (ROOT/'solidworks/evidence/Forearm_native_candidate.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
if __name__=='__main__':main()
