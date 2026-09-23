"""Separate L1 source assembly with rigid hardware groups and six native hinges."""
from leader_parts import *
from build_follower_assembly import sw_transform
from mate_follower import mate_features
from check_assembly_pose import from_sw
from probe_joint_motion import posed_worlds
from scipy.spatial.transform import Rotation
import math
PATH=ROOT/'solidworks/assemblies/SO101_Leader_Master.SLDASM'
EVIDENCE=ROOT/'solidworks/evidence/leader_assembly_build.json'
def connect():
    s=attach();d,e,w=s.OpenDoc6(str(PATH),2,1,'',0,0);assert d is not None,(e,w);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc')
    ev=json.loads(EVIDENCE.read_text());byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)}
    return s,doc,asm,{r['id']:byname[r['name2']] for r in ev['components']}
def main():
    s=attach();m=manifest();w=worlds(m);paths={}
    for i in m['instances']:
        name=i['part'];paths[name]=ROOT/('solidworks/parts/leader' if name.endswith('_Encoder_L1') else 'solidworks/hardware/leader')/(name+'.SLDPRT')
    for name,path in paths.items():
        assert path.exists(),path
        ev=json.loads((ROOT/'solidworks/evidence'/(name+'_leader_part.json')).read_text())
        assert ev['solids'] and all(b['kernel_faults']==0 for b in ev['solids']),('Unaccepted solid',name)
        assert not ev['surface_bodies'] or (ev.get('source_zero_thickness_sheets') and not any(ev['surface_body_faults'])),('Unaccepted surface',name)
    if not PATH.exists():
        for path in paths.values():s.OpenDoc6(str(path),1,1,'',0,0)
        doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplateAssembly),0,0,0));asm=typed(doc,'IAssemblyDoc');ev={'components':[]}
        instances=sorted(m['instances'],key=lambda i:0 if i['part']=='Base_Encoder_L1' else 1)
        for i in instances:
            c=typed(asm.AddComponent5(str(paths[i['part']]),0,'',False,'',0,0,0),'IComponent2');doc.ClearSelection2(True);c.Select4(False,None,False);asm.UnfixComponent();t=w[i['node']]@matrix(i);c.Transform2=sw_transform(s,t)
            if i['part']=='Base_Encoder_L1':doc.ClearSelection2(True);c.Select4(False,None,False);asm.FixComponent()
            ev['components'].append({'id':i['id'],'part':i['part'],'name2':c.Name2,'source_transform_mm':t.tolist(),'grounded':bool(c.IsFixed())})
        assert doc.SaveAs3(str(PATH),0,1)==0;EVIDENCE.write_text(json.dumps(ev,indent=2))
    s,doc,asm,cs=connect();ev=json.loads(EVIDENCE.read_text());ext=typed(doc.Extension,'IModelDocExtension')
    def add(name,kind,angle=0,lo=0,hi=0):
        obj,error=asm.AddMate5(kind,2,False,0,0,0,1,1,angle,hi,lo,False,False,0);assert obj is not None and error==CONST.swAddMateError_NoError,(name,error)
        list(mate_features(doc).values())[-1].Name=name;doc.ClearSelection2(True)
        # Each mate is checkpointed; retaining dozens of CAD undo snapshots of
        # the faceted source parts exhausted this workstation's commit limit.
        doc.ClearUndoList();assert doc.SaveAs3(str(PATH),0,1)==0
        print('Mate',name,flush=True)
    instances=m['instances']
    for i in instances:
        if i['part'].endswith('_Encoder_L1'):continue
        name='Rigid_'+i['id']
        if name in mate_features(doc):continue
        owner=next(a for a in instances if a['node']==i['node'] and a['part'].endswith('_Encoder_L1'))
        doc.ClearSelection2(True);cs[owner['id']].Select4(False,None,False);cs[i['id']].Select4(True,None,False);add(name,CONST.swMateLOCK)
    assert doc.SaveAs3(str(PATH),0,1)==0
    for n in m['nodes']:
        if n['joint'] is None:continue
        j=n['joint'];dat=next(a for a in m['nodes'] if a['id']==n['parent']);parent=next(i for i in instances if i['node']==dat['parent'] and i['part'].endswith('_Encoder_L1'));child=next(i for i in instances if i['node']==n['id'] and i['part'].endswith('_Encoder_L1'));prefix=f'J{j+1}'
        for suffix,a,b,kind,mt in [('Revolute_axis','Axis','Axis','AXIS',CONST.swMateCOINCIDENT),('Axial_location','XY','XY','PLANE',CONST.swMateCOINCIDENT),('Source_preview_limits','YZ','ZX','PLANE',CONST.swMateANGLE)]:
            name=prefix+'_'+suffix
            if name in mate_features(doc):continue
            doc.ClearSelection2(True)
            for k,(i,feature) in enumerate([(parent,a),(child,b)]):
                target=prefix+'_'+feature+'@'+cs[i['id']].Name2+'@'+doc.GetTitle().removesuffix('.SLDASM');assert ext.SelectByID2(target,kind,0,0,0,k>0,1,None,0),target
            add(name,mt,math.pi/2,math.radians(90+m['limits'][j][0]),math.radians(90+m['limits'][j][1]))
        doc.ForceRebuild3(False);assert doc.SaveAs3(str(PATH),0,1)==0
    ev['mates']=[{'name':n,'error':f.GetErrorCode2()} for n,f in mate_features(doc).items()];EVIDENCE.write_text(json.dumps(ev,indent=2));assert all(r['error'][0]==0 for r in ev['mates'])
    doc.ClearSelection2(True);doc.ViewDisplayShaded();doc.ViewZoomtofit2();assert doc.SaveAs3(str(PATH),0,1)==0
    print('Leader assembled:',len(cs),'instances,',len(ev['mates']),'mates',flush=True)
if __name__=='__main__':main()
