from real_limit_mates import *

def main(robot):
 s,d,a,m,build,path=connect_robot(robot);home=[0,-25,35,0,0,20];suffix='_Encoder_L1' if robot=='leader' else '_MG996R_R3';poses={'ZERO':[0]*6,'HOME':home,'MID_RANGE':[0,0,0,0,0,35]}
 rows=[]
 for name,q in ([] if '--verify-only' in sys.argv else {'Default':[0]*6,'ZERO':[0]*6,'MID_RANGE':[0,0,0,0,0,35],'HOME':home}.items()):
  d.ShowConfiguration2(name);fs=mate_features(d);set_pose(d,fs,q,m['limits'],free=False);r=measure(d,a,m,build,name,q);rows.append(r);assert r['kinematic_pass'];assert d.SaveAs3(str(path),0,1)==0
 if 'FREE_MOTION' not in d.GetConfigurationNames():assert d.AddConfiguration3('FREE_MOTION','Six native limited rotational freedoms','',0)
 d.ShowConfiguration2('FREE_MOTION');
 if '--verify-only' not in sys.argv:set_pose(d,mate_features(d),home,m['limits'],free=True)
 r=measure(d,a,m,build,'FREE_MOTION_HOME',home);rows.append(r);assert r['kinematic_pass']
 for name,q in [('ZERO',[0]*6),('MID_RANGE',[0,0,0,0,0,35]),('HOME',home),('FREE_MOTION',home)]:d.ShowConfiguration2(name);d.ForceRebuild3(False);r=measure(d,a,m,build,name+'_REOPEN',q);rows.append(r);assert r['kinematic_pass']
 byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};statuses={i['part']:byname[next(x['name2'] for x in build['components'] if x['id']==i['id'])].GetConstrainedStatus() for i in m['instances'] if i['part'].endswith(suffix)};assert all(v in [CONST.swUnderConstrained,CONST.swFullyConstrained] for v in statuses.values()),statuses
 d.ClearUndoList();assert d.SaveAs3(str(path),0,1)==0;(ROOT/f'solidworks/evidence/{robot}_range_configurations.json').write_text(json.dumps({'configurations':rows,'FREE_MOTION_main_component_native_constraint_status':statuses,'pose_controller_positions':poses,'method':'Fresh CreateMateData/CreateMate, explicit plane entities. Native MateLimitPlanarAngleDim dimensions retain default driving state; optional standard angle pose holders suppressed in FREE_MOTION.'},indent=2));print('Native range setup PASS',robot,flush=True)
if __name__=='__main__':main(sys.argv[1])
