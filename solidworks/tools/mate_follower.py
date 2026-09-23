"""Resume mating the saved follower WIP with inspectable, named native mates."""
from build_follower_assembly import *
def mate_features(doc):
    f=doc.FirstFeature();rows={}
    while f:
        f=typed(f,'IFeature')
        if f.GetTypeName2()=='MateGroup':
            sub=f.GetFirstSubFeature()
            while sub:
                sub=typed(sub,'IFeature');rows[sub.Name]=sub;sub=sub.GetNextSubFeature()
        f=f.GetNextFeature()
    return rows
def main():
    s=attach();path=ROOT/'solidworks/assemblies/SO101_Follower_Reconstruction_WIP.SLDASM'
    d,e,wa=s.OpenDoc6(str(path),2,1,'',0,0);assert d is not None,(e,wa)
    doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc')
    evpath=ROOT/'solidworks/evidence/follower_assembly_build.json';ev=json.loads(evpath.read_text())
    byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)}
    comps={r['id']:byname[r['name2']] for r in ev['components']}
    m=load_manifest();instances=m['instances'];ext=typed(doc.Extension,'IModelDocExtension')
    if 'Lock1' in mate_features(doc):mate_features(doc)['Lock1'].Name='Rigid_follower_sts3215_03a_v1_2'
    if 'Coincident1' in mate_features(doc) and 'J1_Revolute_axis' not in mate_features(doc):mate_features(doc)['Coincident1'].Name='J1_Revolute_axis'
    def add(name,kind,angle=0,lower=0,upper=0):
        if name in mate_features(doc):doc.ClearSelection2(True);return
        obj,error=asm.AddMate5(kind,2,False,0,0,0,1,1,angle,upper,lower,False,False,0)
        row={'name':name,'type':kind,'api_result':error,'success':obj is not None and error==CONST.swAddMateError_NoError}
        ev.setdefault('mate_resume',[]).append(row);evpath.write_text(json.dumps(ev,indent=2));print(row,flush=True)
        assert row['success'],row
        feats=mate_features(doc);feature=list(feats.values())[-1];feature.Name=name
        doc.ClearSelection2(True)
    for i in instances:
        if i['part'].endswith('_MG996R_R3'):continue
        name='Rigid_'+i['id']
        if name in mate_features(doc):continue
        owner=next(a for a in instances if a['node']==i['node'] and a['part'].endswith('_MG996R_R3'))
        doc.ClearSelection2(True);comps[owner['id']].Select4(False,None,False);comps[i['id']].Select4(True,None,False)
        add(name,CONST.swMateLOCK)
    assert doc.SaveAs3(str(path),0,1)==0
    for n in m['nodes']:
        if n['joint'] is None:continue
        j=n['joint'];dat=next(a for a in m['nodes'] if a['id']==n['parent'])
        parent=next(i for i in instances if i['node']==dat['parent'] and i['part'].endswith('_MG996R_R3'))
        child=next(i for i in instances if i['node']==n['id'] and i['part'].endswith('_MG996R_R3'))
        def select_pair(a,b,kind):
            doc.ClearSelection2(True)
            for k,(i,feature) in enumerate([(parent,a),(child,b)]):
                name=feature+'@'+comps[i['id']].Name2+'@'+doc.GetTitle().removesuffix('.SLDASM')
                assert ext.SelectByID2(name,kind,0,0,0,k>0,1,None,0),(name,kind)
        prefix=f'J{j+1}'
        if prefix+'_Revolute_axis' not in mate_features(doc):
            select_pair(prefix+'_Axis',prefix+'_Axis','AXIS');add(prefix+'_Revolute_axis',CONST.swMateCOINCIDENT)
        if prefix+'_Axial_location' not in mate_features(doc):
            select_pair(prefix+'_XY',prefix+'_XY','PLANE');add(prefix+'_Axial_location',CONST.swMateCOINCIDENT)
        if prefix+'_Source_preview_limits' not in mate_features(doc):
            select_pair(prefix+'_YZ',prefix+'_ZX','PLANE');lo,hi=m['limits'][j]
            add(prefix+'_Source_preview_limits',CONST.swMateANGLE,math.pi/2,math.radians(90+lo),math.radians(90+hi))
        doc.ForceRebuild3(False);assert doc.SaveAs3(str(path),0,1)==0
    doc.ClearSelection2(True);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2();doc.ViewDisplayShaded()
    rows=[{'name':name,'type':f.GetTypeName2(),'error':f.GetErrorCode2()} for name,f in mate_features(doc).items()]
    ev['mate_features']=rows;evpath.write_text(json.dumps(ev,indent=2));assert doc.SaveAs3(str(path),0,1)==0
    print(json.dumps({'assembly':str(path),'mates':rows}),flush=True)
if __name__=='__main__':main()
