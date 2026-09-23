"""Repeatable named poses plus a separate six-DOF FREE_MOTION configuration."""
from real_limit_mates import *

def main(robot):
    s,d,a,m,build,path=connect_robot(robot);suffix='_Encoder_L1' if robot=='leader' else '_MG996R_R3';home=[0,-25,35,0,0,20];ext=typed(d.Extension,'IModelDocExtension')
    d.ShowConfiguration2('HOME');fs=mate_features(d)
    if not any(n.endswith('_Pose_driver') for n in fs):set_pose(d,fs,home,m['limits'],force=True)
    byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']}
    for n in m['nodes']:
        if n['joint'] is None:continue
        j=n['joint'];name=f'J{j+1}_Pose_driver'
        if name in mate_features(d):continue
        dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith(suffix));c=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith(suffix));d.ClearSelection2(True)
        for k,(i,plane) in enumerate([(p,'YZ'),(c,'ZX')]):
            target=f'J{j+1}_{plane}@'+cs[i['id']].Name2+'@'+d.GetTitle().removesuffix('.SLDASM');assert ext.SelectByID2(target,'PLANE',0,0,0,k>0,1,None,0),target
        mate,error=a.AddMate5(CONST.swMateANGLE,2,False,0,0,0,1,1,math.radians(90+home[j]),0,0,False,False,0);assert mate is not None and error==CONST.swAddMateError_NoError,(name,error);list(mate_features(d).values())[-1].Name=name;d.ClearSelection2(True);d.ClearUndoList();assert d.SaveAs3(str(path),0,1)==0;print('Added',name,flush=True)
    records=[]
    for name,q in ([] if '--finish' in sys.argv else {'Default':[0]*6,'ZERO':[0]*6,'MID_RANGE':[0,0,0,0,0,35],'HOME':home}.items()):
        d.ShowConfiguration2(name);fs=mate_features(d)
        for j,angle in enumerate(q):
            rangef=fs[f'J{j+1}_Source_preview_limits'];v=typed(rangef.GetDefinition(),'IAngleMateFeatureData');lo,hi=m['limits'][j]
            if not v.IsAdvancedMate or abs(v.MinimumAngle-math.radians(90+lo))>1e-10 or abs(v.MaximumAngle-math.radians(90+hi))>1e-10:
                v.IsAdvancedMate=True;v.MinimumAngle=math.radians(90+lo);v.MaximumAngle=math.radians(90+hi);assert rangef.ModifyDefinition(v,d,None)
            typed(typed(rangef.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension').DrivenState=CONST.swDimensionDriven
            f=fs[f'J{j+1}_Pose_driver'];assert f.SetSuppression2(CONST.swUnSuppressFeature,CONST.swThisConfiguration,None);dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');dim.DrivenState=CONST.swDimensionDriving;assert dim.SetSystemValue3(math.radians(90+angle),CONST.swSetValue_InSpecificConfigurations,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_BSTR,[name]))==0
        d.ForceRebuild3(False);r=measure(d,a,m,build,name,q);records.append(r);assert r['kinematic_pass'];d.ClearUndoList();assert d.SaveAs3(str(path),0,1)==0
    # The controller operates the optional pose holders, while the independent
    # range mates retain mechanical travel bounds.
    feature=typed(a.FeatureByName(robot.title()+'_Joint_Poses'),'IFeature');data=typed(feature.GetDefinition(),'IMateControllerFeatureData');fs=mate_features(d);mates=[typed(fs[f'J{j+1}_Pose_driver'].GetSpecificFeature2(),'IMate2') for j in range(6)]
    poses={'ZERO':[0]*6,'HOME':home,'MID_RANGE':[0,0,0,0,0,35]}
    for j,(lo,hi) in enumerate(m['limits']):
        for label,value in [('MIN',lo),('MAX',hi)]:q=[0]*6;q[j]=value;poses[f'J{j+1}_{label}']=q
    positions={name:np.radians(np.array(q)+90).tolist() for name,q in poses.items()}
    assert data.AccessSelections(d,None);data.Mates=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,mates)
    for name,values in positions.items():
        if name not in data.GetPositions():assert data.AddNewPosition(name)
        data.SetValues(name,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
    assert feature.ModifyDefinition(data,d,None);data=typed(feature.GetDefinition(),'IMateControllerFeatureData');assert all(np.max(abs(np.array(data.GetValues(n))-v))<1e-10 for n,v in positions.items())
    for name,q in [('ZERO',[0]*6),('MID_RANGE',[0,0,0,0,0,35]),('HOME',home)]:
        d.ShowConfiguration2(name);d.ForceRebuild3(False);r=measure(d,a,m,build,name+'_REOPEN',q);records.append(r);assert r['kinematic_pass']
    if 'FREE_MOTION' not in d.GetConfigurationNames():assert d.AddConfiguration3('FREE_MOTION','Six source-bounded rotational freedoms; pose holders suppressed','',0)
    d.ShowConfiguration2('FREE_MOTION');fs=mate_features(d)
    for j in range(6):assert fs[f'J{j+1}_Pose_driver'].SetSuppression2(CONST.swSuppressFeature,CONST.swThisConfiguration,None)
    d.ForceRebuild3(False);r=measure(d,a,m,build,'FREE_MOTION_HOME_START',home);records.append(r);assert r['kinematic_pass'];d.ClearUndoList();assert d.SaveAs3(str(path),0,1)==0
    byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};statuses={i['part']:byname[next(x['name2'] for x in build['components'] if x['id']==i['id'])].GetConstrainedStatus() for i in m['instances'] if i['part'].endswith(suffix)};assert list(statuses.values()).count(CONST.swUnderConstrained)==6,statuses
    report={'configurations':records,'pose_controller_positions':positions,'FREE_MOTION_main_component_native_constraint_status':statuses,'meaning':'ZERO/HOME/MID_RANGE repeatable snapshots use six optional angle holders. FREE_MOTION suppresses holders, retains six native advanced limit-angle mates with driven current dimensions. Six moving main components report native under-constrained status (2); base status 3. This is not mouse-drag certification.'};(ROOT/f'solidworks/evidence/{robot}_range_configurations.json').write_text(json.dumps(report,indent=2));print(robot,'repeatable poses and FREE_MOTION saved.',flush=True)
if __name__=='__main__':main(sys.argv[1])
