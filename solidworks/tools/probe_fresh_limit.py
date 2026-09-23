from real_limit_mates import *
s,d,a,m,build,path=connect_robot('leader');d.ShowConfiguration2('HOME');fs=mate_features(d);ext=typed(d.Extension,'IModelDocExtension');old=fs['J1_Source_preview_limits'];assert old.SetSuppression2(CONST.swSuppressFeature,CONST.swThisConfiguration,None)
byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']};d.ClearSelection2(True)
for k,(id,plane) in enumerate([('leader_follower_Base_Encoder_L1','YZ'),('leader_follower_Shoulder_Encoder_L1','ZX')]):
    assert ext.SelectByID2('J1_'+plane+'@'+cs[id].Name2+'@'+d.GetTitle().removesuffix('.SLDASM'),'PLANE',0,0,0,k>0,1,None,0)
obj,error=a.AddMate5(CONST.swMateANGLE,2,False,0,0,0,1,1,math.pi/2,math.radians(175),math.radians(5),False,False,0);assert obj is not None and error==1,error;f=list(mate_features(d).values())[-1];f.Name='J1_Fresh_Limit_PROBE';d.ClearSelection2(True);d.ForceRebuild3(False)
def details(label):
    v=typed(f.GetDefinition(),'IAngleMateFeatureData');display=f.GetFirstDisplayDimension();dims=[]
    while display is not None:
        display=typed(display,'IDisplayDimension');dim=typed(display.GetDimension2(0),'IDimension');dims.append((dim.FullName,float(np.degrees(dim.SystemValue)),dim.DrivenState));display=f.GetNextDisplayDimension(display)
    print(label,'feature',f.GetTypeName2(),'data',v.IsAdvancedMate,np.degrees([v.Angle,v.MinimumAngle,v.MaximumAngle]).tolist(),'dims',dims,'err',f.GetErrorCode2(),flush=True)
details('fresh')
pose=fs['J1_Pose_driver'];dim=typed(typed(pose.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');assert dim.SetSystemValue3(math.radians(105),CONST.swSetValue_InThisConfiguration,None)==0;d.ForceRebuild3(False);details('q15')
assert pose.SetSuppression2(CONST.swSuppressFeature,CONST.swThisConfiguration,None);d.ForceRebuild3(False);details('free');byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};print('shoulder status',byname['Shoulder_Encoder_L1-1'].GetConstrainedStatus(),flush=True);d.ClearUndoList()
