from real_limit_mates import *

def main(robot):
 s,d,a,m,b,p=connect_robot(robot);d.ShowConfiguration2('HOME');fs=mate_features(d);set_pose(d,fs,[0,-25,35,0,0,20],m['limits'],free=True);r=measure(d,a,m,b,'HOME_BEFORE_REFERENCES',[0,-25,35,0,0,20])
 byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in b['components']};ext=typed(d.Extension,'IModelDocExtension')
 for n in m['nodes']:
  if n['joint'] is None:continue
  j=n['joint'];dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith('_Encoder_L1' if robot=='leader' else '_MG996R_R3'))
  for suffix in ['Source_preview_limits','Pose_driver']:
   f=fs[f'J{j+1}_{suffix}'];v=typed(f.GetDefinition(),'IAngleMateFeatureData');d.ClearSelection2(True);assert ext.SelectByID2(f'J{j+1}_Axis@'+cs[p['id']].Name2+'@'+d.GetTitle().removesuffix('.SLDASM'),'AXIS',0,0,0,False,0,None,0);v.ReferenceEntity=typed(d.SelectionManager,'ISelectionMgr').GetSelectedObject6(1,-1);assert f.ModifyDefinition(v,d,None);print('reference',f.Name,typed(f.GetDefinition(),'IAngleMateFeatureData').ReferenceEntity is not None,flush=True)
  d.ClearUndoList()
 d.ClearSelection2(True);set_pose(d,mate_features(d),[0,-25,35,0,0,20],m['limits'],free=True);d.ForceRebuild3(False);r=measure(d,a,m,b,'HOME_AFTER_REFERENCES',[0,-25,35,0,0,20]);assert r['kinematic_pass']
if __name__=='__main__':main(sys.argv[1])
