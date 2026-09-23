from real_limit_mates import *
s,d,a,m,build,path=connect_robot('leader');d.ShowConfiguration2('HOME');fs=mate_features(d);ext=typed(d.Extension,'IModelDocExtension')
for name in ['J1_Source_preview_limits','J1_Pose_driver']:
 assert fs[name].SetSuppression2(CONST.swSuppressFeature,CONST.swThisConfiguration,None)
d.ForceRebuild3(False)
byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']};d.ClearSelection2(True)
for k,(id,plane) in enumerate([('leader_follower_Base_Encoder_L1','YZ'),('leader_follower_Shoulder_Encoder_L1','ZX')]):
 assert ext.SelectByID2('J1_'+plane+'@'+cs[id].Name2+'@'+d.GetTitle().removesuffix('.SLDASM'),'PLANE',0,0,0,k>0,1,None,0)
raw=a.CreateMateData(CONST.swMateANGLE);v=typed(raw,'IAngleMateFeatureData');v.Angle=math.pi/2;v.MateAlignment=2;v.FlipDimension=False;v.IsAdvancedMate=True;v.MaximumAngle=math.radians(175);v.MinimumAngle=math.radians(5)
sel=typed(d.SelectionManager,'ISelectionMgr');v.EntitiesToMate=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,[sel.GetSelectedObject6(1,1),sel.GetSelectedObject6(2,1)])
print('newdata',v.IsAdvancedMate,np.degrees([v.Angle,v.MinimumAngle,v.MaximumAngle]),flush=True)
obj=a.CreateMate(v);assert obj is not None
f=typed(obj,'IFeature');f.Name='J1_Fresh_Limit_PROBE';d.ClearSelection2(True);d.ForceRebuild3(False)
def details(label):
 v=typed(f.GetDefinition(),'IAngleMateFeatureData');display=f.GetFirstDisplayDimension();dims=[]
 while display is not None:
  display=typed(display,'IDisplayDimension');dim=typed(display.GetDimension2(0),'IDimension');dims.append((dim.FullName,float(np.degrees(dim.SystemValue)),dim.DrivenState));display=f.GetNextDisplayDimension(display)
 print(label,'feature',f.GetTypeName2(),'data',v.IsAdvancedMate,np.degrees([v.Angle,v.MinimumAngle,v.MaximumAngle]).tolist(),'dims',dims,'err',f.GetErrorCode2(),flush=True)
details('fresh')
print('shoulder',byname['Shoulder_Encoder_L1-1'].GetConstrainedStatus(),flush=True)
pose=fs['J1_Pose_driver'];pose.SetSuppression2(CONST.swUnSuppressFeature,CONST.swThisConfiguration,None);dim=typed(typed(pose.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');print('set',dim.SetSystemValue3(math.radians(105),CONST.swSetValue_InThisConfiguration,None),flush=True);d.ForceRebuild3(False);details('q15');print('pose error',pose.GetErrorCode2(),flush=True)
d.ClearUndoList()
