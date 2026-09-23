"""Exercise the actual stdio MCP pose tool and verify the saved native controllers."""
from pathlib import Path
import sys,subprocess,json
ROOT=Path(__file__).resolve().parents[2]
robot=sys.argv[1]
r=subprocess.run([sys.executable,str(ROOT/'solidworks/tools/mcp_call.py'),'set_robot_joint_pose',json.dumps({'robot':robot,'degrees':[0,-25,35,0,0,20],'save':True})],cwd=ROOT,capture_output=True,text=True,check=True)
print(r.stdout,flush=True)
result=json.loads(r.stdout.strip());assert not result.get('isError',False),result
(ROOT/f'solidworks/evidence/{robot}_mcp_pose_handoff.json').write_text(json.dumps(result,indent=2))
from real_limit_mates import *
s,d,a,m,b,p=connect_robot(robot);f=typed(a.FeatureByName(robot.title()+'_Joint_Poses'),'IFeature');v=typed(f.GetDefinition(),'IMateControllerFeatureData');poses={'ZERO':[0]*6,'HOME':[0,-25,35,0,0,20],'MID_RANGE':[0,0,0,0,0,35]}
for j,(lo,hi) in enumerate(m['limits']):
 for name,value in [('MIN',lo),('MAX',hi)]:q=[0]*6;q[j]=value;poses[f'J{j+1}_{name}']=q
actual={name:np.degrees(v.GetValues(name)).tolist() for name in poses};assert all(np.max(abs(np.array(actual[name])-np.array(q)-90))<1e-6 for name,q in poses.items())
(ROOT/f'solidworks/evidence/{robot}_final_controller_positions.json').write_text(json.dumps({'native_degrees':actual,'logical_degrees':poses,'pass':True},indent=2));print(robot,'MCP pose and all 15 saved controller positions PASS',flush=True)
if robot=='leader':s.CloseDoc(d.GetTitle())
else:
 d.ShowConfiguration2('HOME');d.ViewZoomtofit2();d.ClearSelection2(True);d.ClearUndoList();assert d.SaveAs3(str(p),0,1)==0
