"""Add native kinematic datums to preserved solids, without altering source surfaces."""
from sw_api import *
from native_hardware import typed
from audit_sources import matrix
import numpy as np,json,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
def datum(doc,name,t):
    doc.ClearSelection2(True);sm=typed(doc.SketchManager,'ISketchManager');sm.Insert3DSketch(True)
    sm.AddToDB=True;sm.DisplayWhenAdded=False
    origin=t[:3,3]/1000;r=t[:3,:3]
    segments=[]
    for axis in range(3):
        end=origin+r[:,axis]*.01
        line=typed(sm.CreateLine(*origin.tolist(),*end.tolist()),'ISketchSegment')
        doc.ClearSelection2(True);line.Select4(False,None);doc.SketchAddConstraints('sgFIXED');segments.append(line)
        for point,expected in [(typed(typed(line,'ISketchLine').GetStartPoint2(),'ISketchPoint'),origin),(typed(typed(line,'ISketchLine').GetEndPoint2(),'ISketchPoint'),end)]:
            assert np.max(np.abs(np.array([point.X,point.Y,point.Z])-expected))<1e-11,'Sketch inference moved a datum'
    sm.DisplayWhenAdded=True;sm.AddToDB=False
    sm.Insert3DSketch(True)
    sk=typed(doc.FeatureByPositionReverse(0),'IFeature');sk.Name=name+'_Frame'
    doc.ClearSelection2(True);segments[2].Select4(False,None)
    assert doc.InsertAxis2(True),name
    af=typed(doc.FeatureByPositionReverse(0),'IFeature');af.Name=name+'_Axis'
    points=[typed(typed(seg,'ISketchLine').GetEndPoint2(),'ISketchPoint') for seg in segments]
    point0=typed(typed(segments[0],'ISketchLine').GetStartPoint2(),'ISketchPoint')
    sel=typed(doc.SelectionManager,'ISelectionMgr')
    fm=typed(doc.FeatureManager,'IFeatureManager')
    for plane,a,b in [('XY',0,1),('YZ',1,2),('ZX',2,0)]:
        doc.ClearSelection2(True)
        for mark,point in enumerate([point0,points[a],points[b]]):
            sd=typed(sel.CreateSelectData(),'ISelectData');sd.Mark=mark;assert point.Select4(True,sd)
        result=fm.InsertRefPlane(4,0,4,0,4,0)
        assert result is not None,(name,plane)
        pf=typed(doc.FeatureByPositionReverse(0),'IFeature');pf.Name=name+'_'+plane
    doc.ClearSelection2(True);sk.Select2(False,0);doc.BlankSketch();doc.ClearSelection2(True)
def load_manifest():
    m=json.loads((ROOT/'robot-studio/public/models/so101/study-manifest.json').read_text())
    m['nodes']=[n for n in m['nodes'] if n['id'].startswith('follower')]
    m['instances']=[i for i in m['instances'] if i['robot']=='follower']
    m['nodes'][0]['position'][0]=0
    return m
def worlds(m):
    w={}
    for n in m['nodes']:w[n['id']]=(w[n['parent']] if n['parent'] else np.eye(4))@matrix(n)
    return w
def main(only=None,rebuild=False):
    s=attach();m=load_manifest();w=worlds(m)
    parts=[i for i in m['instances'] if i['part'].endswith('_MG996R_R3')]
    log=[]
    for i in parts:
        if only and only not in i['part']:continue
        dest=ROOT/'solidworks/parts'/(i['part']+'.SLDPRT')
        if dest.exists():
            if not rebuild:print('Already prepared',dest.name,flush=True);continue
            s.CloseDoc(str(dest))
            backup=ROOT/'solidworks/checkpoints/pre_inference_fix';backup.mkdir(exist_ok=True)
            if not (backup/dest.name).exists():shutil.copy2(dest,backup/dest.name)
        source=ROOT/'solidworks/checkpoints/mesh_reference'/(i['part']+'_REFERENCE.SLDPRT')
        if i['part']=='Forearm_MG996R_R3':
            source=ROOT/'solidworks/checkpoints/Forearm_R3_final_healed.SLDPRT'
        d,e,wa=s.OpenDoc6(str(source),1,1,'',0,0);assert d is not None,(source,e)
        doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0)
        assert doc.SaveAs3(str(dest),0,1)==0
        pworld=w[i['node']]@matrix(i)
        added=[]
        for n in m['nodes']:
            if n['joint'] is None:continue
            fixed=next(a for a in m['nodes'] if a['id']==n['parent'])
            if i['node'] not in [n['id'],fixed['parent']]:continue
            name='J'+str(n['joint']+1)
            t=np.linalg.inv(pworld)@w[n['id']]
            print('Datum',i['part'],name,flush=True);datum(doc,name,t);added.append({'name':name,'matrix_mm':t.tolist()})
        doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,[.8,.25,.07,1,.5,.25,.1,0,0])
        doc.ForceRebuild3(False);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2()
        assert doc.SaveAs3(str(dest),0,1)==0
        solid_count=len(typed(doc,'IPartDoc').GetBodies2(0,False) or [])
        surface_count=len(typed(doc,'IPartDoc').GetBodies2(1,False) or [])
        row={'part':i['part'],'path':str(dest),'geometry':'source import with native reference sketches, axes and planes','solid_bodies':solid_count,'surface_bodies':surface_count,'status':'WIP surface reference, solid reconstruction required' if not solid_count else 'Imported solid reference; parametric reconstruction incomplete','datums':added,'sketch_inference_disabled':True,'datum_coordinates_readback_checked':True}
        (ROOT/'solidworks/evidence'/(i['part']+'_datums.json')).write_text(json.dumps(row,indent=2));log.append(row)
        s.CloseDoc(doc.GetTitle())
    print(json.dumps({'prepared':[r['part'] for r in log]}))
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith('--') else None,'--rebuild' in sys.argv)
