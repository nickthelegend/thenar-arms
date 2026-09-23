"""Editable SolidWorks nominal hardware from the current R3 source dimensions."""
from sw_api import *
import json, math,shutil
ROOT=Path(__file__).resolve().parents[2]
def typed(obj,name):return getattr(SW,name)(obj._oleobj_)
def sketch(doc,name,rect=None,circles=()):
    doc.ClearSelection2(True)
    ext=typed(doc.Extension,'IModelDocExtension')
    assert ext.SelectByID2('Front Plane','PLANE',0,0,0,False,0,None,0)
    sm=typed(doc.SketchManager,'ISketchManager');sm.InsertSketch(True)
    sm.AddToDB=True;sm.DisplayWhenAdded=False
    if rect:
        x0,y0,x1,y1=rect;sm.CreateCornerRectangle(x0/1000,y0/1000,0,x1/1000,y1/1000,0)
    for x,y,r in circles:sm.CreateCircleByRadius(x/1000,y/1000,0,r/1000)
    # Freeze the source profile coordinates with native fixed sketch relations.
    sm.DisplayWhenAdded=True;sm.AddToDB=False
    doc.SketchAddConstraints('sgFIXED')
    sm.InsertSketch(True)
    f=doc.FeatureByPositionReverse(0);f=typed(f,'IFeature');f.Name=name
    doc.ClearSelection2(True);assert f.Select2(False,0)
    return f
def boss(doc,name,z0,z1,rect=None,circles=()):
    sketch(doc,name+'_Profile',rect,circles)
    fm=typed(doc.FeatureManager,'IFeatureManager')
    f=fm.FeatureExtrusion3(True,False,False,0,0,(z1-z0)/1000,0,False,False,False,False,0,0,False,False,False,False,True,True,True,3,abs(z0)/1000,z0<0)
    assert f is not None,name
    typed(f,'IFeature').Name=name
    return f
def make(which):
    s=attach()
    expected='MG996R_Nominal_R3' if which=='MG996R' else 'Metal_Horn_D20_PCD14_R3'
    old=ROOT/'solidworks/hardware'/(expected+'.SLDPRT')
    if old.exists():
        checkpoint=ROOT/'solidworks/checkpoints/pre_inference_fix';checkpoint.mkdir(exist_ok=True)
        if not (checkpoint/old.name).exists():shutil.copy2(old,checkpoint/old.name)
        s.CloseDoc(str(old))
    doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0))
    if which=='MG996R':
        boss(doc,'Case_40p9_x_20_x_37',-28.5,8.5,(-18.4,-10,22.5,10))
        boss(doc,'Mounting_tabs_54_x_20_x_2p6',-1.7,.9,(-24.95,-10,29.05,10))
        boss(doc,'Output_boss_D13',8.5,11.5,circles=[(12.5,0,6.5)])
        boss(doc,'Output_shaft_envelope_D6',8.5,14.2,circles=[(12.5,0,3)])
        name='MG996R_Nominal_R3';color=[.12,.14,.17,1,.5,.3,.15,0,0]
    elif which=='horn':
        # Annular hub and disc. Source hole is 2.5 mm tap-drill envelope, no invented thread.
        boss(doc,'Spline_hub_envelope',12.2,14.2,circles=[(12.5,0,5.5),(12.5,0,2.75)])
        boss(doc,'Disc_D20_PCD14_tap_drills',14.2,16.7,circles=[(12.5,0,10),(12.5,0,2.75)]+[(12.5+x,y,1.25) for x,y in [(7,0),(-7,0),(0,7),(0,-7)]])
        name='Metal_Horn_D20_PCD14_R3';color=[.72,.56,.25,1,.6,.5,.35,0,0]
    else:raise ValueError(which)
    doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,color)
    doc.ForceRebuild3(False);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2()
    path=ROOT/'solidworks/hardware'/(name+'.SLDPRT')
    error=doc.SaveAs3(str(path),0,1);assert error==0,error
    bodies=typed(doc,'IPartDoc').GetBodies2(0,False)
    f=doc.FirstFeature();features=[]
    while f:
        f=typed(f,'IFeature');features.append({'name':f.Name,'type':f.GetTypeName2()});f=f.GetNextFeature()
    evidence={'path':str(path),'save_error':error,'body_count':len(bodies or []),'features':features,'native_features':True,'source':'build_follower_r3.py servo()/metal_horn(); nominal not measured hardware','bodies':[{'box_m':list(typed(b,'IBody2').GetBodyBox()),'mass_properties_density_1':list(typed(b,'IBody2').GetMassProperties(1))} for b in bodies or []]}
    (ROOT/'solidworks/evidence'/(name+'.json')).write_text(json.dumps(evidence,indent=2))
    return evidence
if __name__=='__main__':
    import sys;print(json.dumps(make(sys.argv[1])))
