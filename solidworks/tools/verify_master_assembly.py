"""Reopen a delivered master, verify stored poses/references, save HOME view."""
from check_assembly_pose import *
from probe_joint_motion import posed_worlds
from leader_parts import manifest as leader_manifest
from PIL import Image
import sys

def main(robot):
    assert robot in ['follower','leader'];s=attach();path=ROOT/'solidworks/assemblies'/f'SO101_{robot.title()}_Master.SLDASM'
    # Caller closes the other task-owned assembly first to limit memory use.
    existing=s.GetOpenDocumentByName(str(path))
    if existing is not None:assert not model(existing).GetSaveFlag(),'Save accepted work before reopen verification';s.CloseDoc(model(existing).GetTitle())
    d,e,w=s.OpenDoc6(str(path),2,1,'',0,0);assert d is not None,(e,w);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc')
    m=leader_manifest() if robot=='leader' else load_manifest();build=json.loads((ROOT/f'solidworks/evidence/{robot}_assembly_build.json').read_text());rows=[]
    for name,q in [('ZERO',[0]*6),('MID_RANGE',[0,0,0,0,0,35]),('HOME',[0,-25,35,0,0,20])]:
        doc.ShowConfiguration2(name);assert typed(typed(doc.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name==name
        doc.ForceRebuild3(False);world=posed_worlds(m,q);byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']};components=[]
        for i in m['instances']:
            a=from_sw(cs[i['id']]);b=world[i['node']]@matrix(i);components.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-b[:3,3])),'angle_error_deg':float(np.degrees(Rotation.from_matrix(b[:3,:3].T@a[:3,:3]).magnitude())),'fixed':bool(cs[i['id']].IsFixed())})
        errors=[{'name':n,'error':f.GetErrorCode2()} for n,f in mate_features(doc).items() if f.GetErrorCode2()[0]!=0]
        r={'configuration':name,'components':components,'mate_errors':errors,'max_position_error_mm':max(x['position_error_mm'] for x in components),'max_angle_error_deg':max(x['angle_error_deg'] for x in components),'fixed_count':sum(x['fixed'] for x in components)};r['pass']=not errors and r['fixed_count']==1 and max(r['max_position_error_mm'],r['max_angle_error_deg'])<.001;rows.append(r)
        r['native_limits']=[]
        for j,(lo,hi) in enumerate(m['limits']):
            f=mate_features(doc)[f'J{j+1}_Source_preview_limits'];v=typed(f.GetDefinition(),'IAngleMateFeatureData');dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');r['native_limits'].append({'joint':j+1,'advanced':bool(v.IsAdvancedMate),'lower_degrees':float(np.degrees(v.MinimumAngle)-90),'upper_degrees':float(np.degrees(v.MaximumAngle)-90),'active':not f.IsSuppressed(),'current_angle_driven_state':dim.DrivenState});assert v.IsAdvancedMate and abs(np.degrees(v.MinimumAngle)-90-lo)<1e-6 and abs(np.degrees(v.MaximumAngle)-90-hi)<1e-6 and dim.DrivenState==CONST.swDimensionDriving
        print({k:v for k,v in r.items() if k not in ['components','native_limits']},flush=True);assert r['pass'];doc.ClearUndoList()
    controller=typed(typed(asm.FeatureByName(robot.title()+'_Joint_Poses'),'IFeature').GetDefinition(),'IMateControllerFeatureData')
    expected_positions={'ZERO':[0]*6,'HOME':[0,-25,35,0,0,20],'MID_RANGE':[0,0,0,0,0,35]}
    for j,(lo,hi) in enumerate(m['limits']):
        for label,val in [('MIN',lo),('MAX',hi)]:q=[0]*6;q[j]=val;expected_positions[f'J{j+1}_{label}']=q
    controller_positions={name:np.degrees(controller.GetValues(name)).tolist() for name in expected_positions}
    assert all(np.max(abs(np.array(controller_positions[name])-np.array(q)-90))<1e-6 for name,q in expected_positions.items())
    parts={}
    for c in cs.values():
        filename=c.GetPathName()
        if filename in parts:continue
        p=typed(c.GetModelDoc2(),'IPartDoc');solids=[typed(b,'IBody2').Check2() for b in p.GetBodies2(0,False) or []];sheets=[typed(b,'IBody2').Check2() for b in p.GetBodies2(1,False) or []];assert solids and not any(solids+sheets),(filename,solids,sheets);parts[filename]={'solid_faults':solids,'surface_faults':sheets}
    limits=[]
    for j,(lo,hi) in enumerate(m['limits']):
        a=typed(mate_features(doc)[f'J{j+1}_Source_preview_limits'].GetDefinition(),'IAngleMateFeatureData');r={'joint':j+1,'logical_min_deg':float(np.degrees(a.MinimumAngle)-90),'logical_max_deg':float(np.degrees(a.MaximumAngle)-90)};assert abs(r['logical_min_deg']-lo)<1e-6 and abs(r['logical_max_deg']-hi)<1e-6;limits.append(r)
    # Named snapshots use optional pose holders; FREE_MOTION keeps only the
    # actual six range-limited hinges and the rigid hardware connections.
    doc.ShowConfiguration2('FREE_MOTION');doc.ForceRebuild3(False)
    for j in range(6):
        assert mate_features(doc)[f'J{j+1}_Pose_driver'].IsSuppressed()
        assert not mate_features(doc)[f'J{j+1}_Source_preview_limits'].IsSuppressed()
    wrong_count=typed(doc.Extension,'IModelDocExtension').GetWhatsWrongCount();assert wrong_count==0,('Native rebuild diagnostic',wrong_count)
    doc.ClearSelection2(True);doc.SetUserPreferenceToggle(CONST.swViewDisplayHideAllTypes,True);v=typed(doc.ActiveView,'IModelView');z=np.array([1.,-1.,.8]);z/=np.linalg.norm(z);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);t=np.eye(4);t[:3,:3]=[x,y,z];v.Orientation3=sw_transform(s,t);doc.NameView('SOURCE_Z_UP');doc.ViewDisplayShaded();doc.ViewZoomtofit2();doc.ClearUndoList();assert doc.SaveAs3(str(path),0,1)==0
    imagepath=ROOT/f'solidworks/evidence/{robot}_HOME.bmp';assert doc.SaveBMP(str(imagepath),1600,1200);Image.open(imagepath).save(imagepath.with_suffix('.png'))
    report={'assembly':str(path),'pose_controller_positions_native_degrees':controller_positions,'configurations':rows,'parts':parts,'limits':limits,'component_count':len(cs),'mate_count':len(mate_features(doc)),'active_mate_count_FREE_MOTION':sum(not f.IsSuppressed() for f in mate_features(doc).values()),'native_rebuild_diagnostic_count':wrong_count,'solid_body_count_unique_parts':sum(len(p['solid_faults']) for p in parts.values()),'surface_body_count_unique_parts':sum(len(p['surface_faults']) for p in parts.values()),'status':'PASS; configurations, mate errors, limits, loaded-reference body kernel checks; free mouse drag not tested'}
    (ROOT/f'verification/{robot}_master_reopen.json').write_text(json.dumps(report,indent=2));print('Saved verified HOME master and native CAD viewport image.',flush=True)
if __name__=='__main__':main(sys.argv[1])
