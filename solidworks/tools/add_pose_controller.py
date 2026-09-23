"""Named native mate-controller positions, using the verified source joint convention."""
from check_assembly_pose import *

def main():
    s,doc,asm,cs=connect();m=load_manifest();fm=typed(doc.FeatureManager,'IFeatureManager')
    existing=asm.FeatureByName('Follower_Joint_Poses')
    names=[f'J{j+1}_Source_preview_limits' for j in range(6)]
    feats=mate_features(doc);mates=[typed(feats[name].GetSpecificFeature2(),'IMate2') for name in names]
    data=typed(fm.CreateDefinition(CONST.swFmMateController),'IMateControllerFeatureData') if existing is None else typed(typed(existing,'IFeature').GetDefinition(),'IMateControllerFeatureData')
    if existing is None:data.Initialize(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,mates))
    poses={'ZERO':[0]*6,'HOME':[0,-25,35,0,0,20],'MID_RANGE':[0,0,0,0,0,35]}
    for j,(lo,hi) in enumerate(m['limits']):
        for suffix,value in [('MIN',lo),('MAX',hi)]:
            q=[0]*6;q[j]=value;poses[f'J{j+1}_{suffix}']=q
    if existing is None:
        for name,q in poses.items():
            assert data.AddNewPosition(name),name
            data.SetValues(name,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,[math.radians(90+a) for a in q]))
    feature=fm.CreateFeature(data) if existing is None else existing;assert feature is not None,fm.GetCreateFeatureErrors()
    feature=typed(feature,'IFeature');feature.Name='Follower_Joint_Poses'
    data=typed(feature.GetDefinition(),'IMateControllerFeatureData')
    rows={name:list(data.GetValues(name)) for name in data.GetPositions()}
    print(rows,flush=True)
    for name,q in poses.items():assert np.max(np.abs(np.array(rows[name])-np.radians(np.array(q)+90)))<1e-10,name
    assert doc.SaveAs3(doc.GetPathName(),0,1)==0
    data.AccessSelections(doc,None)
    configs={name:bool(data.AddConfigurationFromPosition(name,False)) for name in ['ZERO','HOME','MID_RANGE']}
    assert feature.ModifyDefinition(data,doc,None),'Commit configuration creation failed'
    actual_configs=list(doc.GetConfigurationNames())
    print('configs',configs,flush=True)
    if all(configs.values()):doc.ShowConfiguration2('HOME')
    doc.ForceRebuild3(False);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2()
    assert doc.SaveAs3(doc.GetPathName(),0,1)==0
    (ROOT/'solidworks/evidence/mate_controller.json').write_text(json.dumps({'feature':'Follower_Joint_Poses','source_joint_degrees':poses,'stored_native_mate_radians':rows,'configuration_api_results':configs,'actual_configuration_names':actual_configs},indent=2))
if __name__=='__main__':main()
