from real_limit_mates import *
s,d,a,m,b,p=connect_robot('follower');r=measure(d,a,m,b,'FOLLOWER_BRANCH',[0,-25,35,0,0,20]);print(r['joints']);print([(n,typed(f.GetDefinition(),'IAngleMateFeatureData').MateAlignment,typed(f.GetDefinition(),'IAngleMateFeatureData').FlipDimension) for n,f in mate_features(d).items() if n.endswith('driver') or n.endswith('limits')])
