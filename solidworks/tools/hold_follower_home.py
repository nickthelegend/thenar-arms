from real_limit_mates import *
s,d,a,m,b,p=connect_robot('follower');d.ShowConfiguration2('HOME');set_pose(d,mate_features(d),[0,-25,35,0,0,20],m['limits'],free=False);r=measure(d,a,m,b,'HELD_HOME',[0,-25,35,0,0,20]);print(r['joints'])
