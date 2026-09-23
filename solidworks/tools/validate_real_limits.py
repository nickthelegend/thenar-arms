"""Final native range-mate validation, preserving all six rotational freedoms."""
from real_limit_mates import *

def main(robot):
    s,d,a,m,build,path=connect_robot(robot)
    if 'FREE_MOTION' in d.GetConfigurationNames():d.ShowConfiguration2('FREE_MOTION')
    backup=ROOT/f'solidworks/checkpoints/{robot}_before_final_range_validation.SLDASM'
    if not backup.exists():shutil.copy2(path,backup)
    poses={'ZERO':[0]*6}
    for j,(lo,hi) in enumerate(m['limits']):
        for suffix,val in [('MIN',lo),('ZERO_AFTER_MIN',0),('MAX',hi),('ZERO_AFTER_MAX',0)]:q=[0]*6;q[j]=val;poses[f'J{j+1}_{suffix}']=q
    poses.update(HOME=[0,-25,35,0,0,20],MULTI=[20,-30,40,-20,30,25],ZERO_FINAL=[0]*6);rows=[];fs=mate_features(d)
    out=ROOT/f'solidworks/evidence/{robot}_limit_motion_measurements.json'
    for name,q in poses.items():
        set_pose(d,fs,q,m['limits'],free=True);r=measure(d,a,m,build,name,q);rows.append(r);out.write_text(json.dumps(rows,indent=2));assert r['kinematic_pass']
    original=ROOT/('solidworks/evidence/leader_joint_motion_measurements.json' if robot=='leader' else 'solidworks/evidence/joint_motion_measurements.json');cp=ROOT/f'solidworks/checkpoints/{robot}_fixed_angle_pose_measurements.json'
    if not cp.exists():shutil.copy2(original,cp)
    original.write_text(json.dumps(rows,indent=2))
    set_pose(d,mate_features(d),[0,-25,35,0,0,20],m['limits'],free=True)
    assert d.SaveAs3(str(path),0,1)==0
    print(robot,'28 range-mate poses and stored configurations passed.',flush=True)
if __name__=='__main__':main(sys.argv[1])
