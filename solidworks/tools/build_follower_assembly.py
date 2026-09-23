"""Source-transform assembly with real joint/rigid-group mates; verification is separate."""
from sw_api import *
from native_hardware import typed
from prepare_follower_parts import load_manifest,worlds,ROOT,matrix
import numpy as np,json,math
def sw_transform(s,t):
    a=t[:3,:3].T.flatten().tolist()+(t[:3,3]/1000).tolist()+[1.,0.,0.,0.]
    result=typed(s.GetMathUtility(),'IMathUtility').CreateTransform(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,a))
    assert np.max(np.abs(np.array(typed(result,'IMathTransform').ArrayData)-a))<1e-12,'Transform marshalling failed'
    return result
def main():
    s=attach();m=load_manifest();w=worlds(m)
    assembly_path=ROOT/'solidworks/assemblies/SO101_Follower_Reconstruction_WIP.SLDASM'
    if assembly_path.exists():raise RuntimeError('Refusing to overwrite assembly checkpoint; continue existing assembly explicitly')
    paths={i['part']:ROOT/'solidworks/parts'/(i['part']+'.SLDPRT') for i in m['instances'] if i['part'].endswith('_MG996R_R3')}
    paths.update(MG996R_body_R3=ROOT/'solidworks/hardware/MG996R_Nominal_R3.SLDPRT',metal_horn_R3=ROOT/'solidworks/hardware/Metal_Horn_D20_PCD14_R3.SLDPRT')
    for path in paths.values():assert path.exists(),path
    for path in paths.values():
        d,e,wa=s.OpenDoc6(str(path),1,1,'',0,0);assert d is not None,(path,e)
    doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplateAssembly),0,0,0))
    asm=typed(doc,'IAssemblyDoc');components={};evidence={'components':[],'mates':[]}
    # The base is inserted first; it is the sole grounded component.
    instances=sorted(m['instances'],key=lambda i:0 if i['part']=='Base_MG996R_R3' else 1)
    for i in instances:
        c=asm.AddComponent5(str(paths[i['part']]),0,'',False,'',0,0,0);assert c is not None,i
        c=typed(c,'IComponent2');c.Name2=i['id'];doc.ClearSelection2(True);c.Select4(False,None,False);asm.UnfixComponent()
        t=w[i['node']]@matrix(i);c.Transform2=sw_transform(s,t)
        if i['part']=='Base_MG996R_R3':doc.ClearSelection2(True);c.Select4(False,None,False);asm.FixComponent()
        components[i['id']]=c
        evidence['components'].append({'id':i['id'],'name2':c.Name2,'source_transform_mm':t.tolist(),'sw_transform':list(typed(c.Transform2,'IMathTransform').ArrayData),'grounded':bool(c.IsFixed())})
    assert doc.SaveAs3(str(assembly_path),0,1)==0
    (ROOT/'solidworks/evidence/follower_assembly_build.json').write_text(json.dumps(evidence,indent=2))
    def mate(name,kind,angle=0,lower=0,upper=0):
        result=asm.AddMate5(kind,2,False,0,0,0,1,1,angle,upper,lower,False,False,0)
        obj,error=result if isinstance(result,tuple) else (result,None)
        evidence['mates'].append({'name':name,'type':kind,'error':error,'created':obj is not None})
        (ROOT/'solidworks/evidence/follower_assembly_build.json').write_text(json.dumps(evidence,indent=2))
        print('Mate',name,error,obj is not None,flush=True)
        assert obj is not None and error==CONST.swAddMateError_NoError,(name,error)
        feature=typed(doc.FeatureByPositionReverse(0),'IFeature')
        if feature.GetTypeName2()=='MateGroup':
            sub=feature.GetFirstSubFeature()
            while sub:
                feature=typed(sub,'IFeature');sub=feature.GetNextSubFeature()
        feature.Name=name
        doc.ClearSelection2(True)
        return obj
    # Purchased hardware is rigid to its correct link, not grounded globally.
    for i in instances:
        if i['part'].endswith('_MG996R_R3'):continue
        owner=next(a for a in instances if a['node']==i['node'] and a['part'].endswith('_MG996R_R3'))
        doc.ClearSelection2(True);components[owner['id']].Select4(False,None,False);components[i['id']].Select4(True,None,False)
        mate('Rigid_'+i['id'],CONST.swMateLOCK)
    ext=typed(doc.Extension,'IModelDocExtension')
    for n in m['nodes']:
        if n['joint'] is None:continue
        j=n['joint'];dat=next(a for a in m['nodes'] if a['id']==n['parent'])
        parent=next(i for i in instances if i['node']==dat['parent'] and i['part'].endswith('_MG996R_R3'))
        child=next(i for i in instances if i['node']==n['id'] and i['part'].endswith('_MG996R_R3'))
        def select_pair(pa,ch,kind):
            doc.ClearSelection2(True)
            for k,(i,feature) in enumerate([(parent,pa),(child,ch)]):
                name=feature+'@'+components[i['id']].Name2+'@'+doc.GetTitle().split('.')[0]
                assert ext.SelectByID2(name,kind,0,0,0,k>0,1,None,0),(name,kind)
        prefix=f'J{j+1}'
        select_pair(prefix+'_Axis',prefix+'_Axis','AXIS');mate(prefix+'_Revolute_axis',CONST.swMateCOINCIDENT)
        select_pair(prefix+'_XY',prefix+'_XY','PLANE');mate(prefix+'_Axial_location',CONST.swMateCOINCIDENT)
        # Parent +X vs child +Y normal: 90deg+q, stays away from ambiguous 0/180.
        select_pair(prefix+'_YZ',prefix+'_ZX','PLANE')
        lo,hi=m['limits'][j]
        mate(prefix+'_Source_preview_limits',CONST.swMateANGLE,math.pi/2,math.radians(90+lo),math.radians(90+hi))
    doc.ForceRebuild3(False);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2();doc.ClearSelection2(True)
    error=doc.SaveAs3(str(assembly_path),0,1);evidence['save_error']=error
    (ROOT/'solidworks/evidence/follower_assembly_build.json').write_text(json.dumps(evidence,indent=2))
    assert error==0,error
    print(json.dumps({'assembly':str(assembly_path),'components':len(components),'mates':len(evidence['mates'])}))
if __name__=='__main__':main()
