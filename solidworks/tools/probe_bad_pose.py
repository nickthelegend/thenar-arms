from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');r=measure(d,a,m,b,'DEBUG_DEFAULT',[0]*6);print(r['joints']);print(r['native_limits']);print([(c['id'],round(c['angle_error_deg'],3)) for c in r['components'] if c['angle_error_deg']>.001]);print([(n,typed(f.GetDefinition(),'IAngleMateFeatureData').MateAlignment) for n,f in mate_features(d).items() if n.endswith('limits')])
