"""Create genuine native limit mates using explicit mate entities, never convert fixed angles."""
from real_limit_mates import *

def main(robot):
 s,d,a,m,build,path=connect_robot(robot);home=[0,-25,35,0,0,20];suffix='_Encoder_L1' if robot=='leader' else '_MG996R_R3';d.ShowConfiguration2('HOME');ext=typed(d.Extension,'IModelDocExtension');cp=ROOT/f'solidworks/checkpoints/{robot}_before_native_limit_replacement.SLDASM'
 if not cp.exists():shutil.copy2(path,cp)
 controller=a.FeatureByName(robot.title()+'_Joint_Poses')
 fs=mate_features(d)
 for name in list(fs):
  if name.endswith('_Source_preview_limits'):
   j=name.split('_')[0]
   if j+'_Pose_driver' not in fs:
    fs[name].Name=j+'_Pose_driver'
   else:
    d.ClearSelection2(True);assert fs[name].Select2(False,0);assert ext.DeleteSelection2(0)
 d.ForceRebuild3(False);d.ClearUndoList()
 byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']}
 for n in m['nodes']:
  if n['joint'] is None:continue
  j=n['joint'];dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith(suffix));c=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith(suffix))
  def select():
   d.ClearSelection2(True)
   for k,(i,plane) in enumerate([(p,'YZ'),(c,'ZX')]):assert ext.SelectByID2(f'J{j+1}_{plane}@'+cs[i['id']].Name2+'@'+d.GetTitle().removesuffix('.SLDASM'),'PLANE',0,0,0,k>0,1,None,0)
  select();v=typed(a.CreateMateData(CONST.swMateANGLE),'IAngleMateFeatureData');v.Angle=math.radians(90+home[j]);v.MateAlignment=2;v.FlipDimension=False;v.IsAdvancedMate=True;v.MaximumAngle=math.radians(90+m['limits'][j][1]);v.MinimumAngle=math.radians(90+m['limits'][j][0]);sel=typed(d.SelectionManager,'ISelectionMgr');v.EntitiesToMate=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,[sel.GetSelectedObject6(1,1),sel.GetSelectedObject6(2,1)]);obj=a.CreateMate(v);assert obj is not None,(robot,j);f=typed(obj,'IFeature');f.Name=f'J{j+1}_Source_preview_limits';assert f.GetTypeName2()=='MateLimitPlanarAngleDim';assert f.SetSuppression2(CONST.swUnSuppressFeature,CONST.swAllConfiguration,None)
  if f'J{j+1}_Pose_driver' not in mate_features(d):
   select();obj,err=a.AddMate5(CONST.swMateANGLE,2,False,0,0,0,1,1,math.radians(90+home[j]),0,0,False,False,0);assert obj is not None and err==1,err;list(mate_features(d).values())[-1].Name=f'J{j+1}_Pose_driver'
  d.ClearSelection2(True);d.ForceRebuild3(False);d.ClearUndoList();print(robot,'created genuine range',j+1,flush=True)
 fs=mate_features(d);set_pose(d,fs,home,m['limits'],free=False)
 fm=typed(d.FeatureManager,'IFeatureManager');data=typed(fm.CreateDefinition(CONST.swFmMateController),'IMateControllerFeatureData') if controller is None else typed(typed(controller,'IFeature').GetDefinition(),'IMateControllerFeatureData');mates=[typed(fs[f'J{j+1}_Pose_driver'].GetSpecificFeature2(),'IMate2') for j in range(6)];
 if controller is None:data.Initialize(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,mates))
 else:
  assert data.AccessSelections(d,None);data.Mates=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,mates)
 poses={'ZERO':[0]*6,'HOME':home,'MID_RANGE':[0,0,0,0,0,35]}
 for j,(lo,hi) in enumerate(m['limits']):
  for label,value in [('MIN',lo),('MAX',hi)]:q=[0]*6;q[j]=value;poses[f'J{j+1}_{label}']=q
 for name,q in poses.items():
  if name not in (data.GetPositions() or []):assert data.AddNewPosition(name)
  data.SetValues(name,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,np.radians(np.array(q)+90).tolist()))
 if controller is None:f=typed(fm.CreateFeature(data),'IFeature');f.Name=robot.title()+'_Joint_Poses'
 else:assert typed(controller,'IFeature').ModifyDefinition(data,d,None)
 from add_angle_reference_axes import main as refs
 refs(robot)
 from finish_native_limit_configurations import main as finish
 finish(robot)
if __name__=='__main__':main(sys.argv[1])
