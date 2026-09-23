"""Set a source-defined pose using native mates, retaining verified range bounds."""
from real_limit_mates import *
import argparse
p=argparse.ArgumentParser();p.add_argument('robot',choices=['follower','leader']);p.add_argument('angles',nargs=6,type=float,metavar='DEG');p.add_argument('--save',action='store_true');args=p.parse_args()
s,d,a,m,build,path=connect_robot(args.robot)
assert 'FREE_MOTION' in d.GetConfigurationNames(),'Finish master configuration setup first'
d.ShowConfiguration2('FREE_MOTION')
for angle,(lo,hi) in zip(args.angles,m['limits']):assert np.isfinite(angle) and lo<=angle<=hi,('Outside source software limits',angle,lo,hi)
set_pose(d,mate_features(d),args.angles,m['limits'],force=True);r=measure(d,a,m,build,'REQUESTED',args.angles);assert r['kinematic_pass'];d.ViewZoomtofit2()
if args.save:assert d.SaveAs3(str(path),0,1)==0
print('Source bounds retained; pose is not a physical clearance certification.')
