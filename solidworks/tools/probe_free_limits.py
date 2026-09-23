from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');set_pose(d,mate_features(d),[0]*6,m['limits'],free=True);r=measure(d,a,m,b,'ZERO_RELEASED',[0]*6);print('errors',r['mate_errors']);print('limits',r['native_limits']);print('diagnostics',typed(d.Extension,'IModelDocExtension').GetWhatsWrongCount())
