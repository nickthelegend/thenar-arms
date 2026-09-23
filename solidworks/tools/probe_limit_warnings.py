from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');r=measure(d,a,m,b,'ZERO_DEBUG',[0]*6);print(r['native_limits']);print('whatswrong',typed(d.Extension,'IModelDocExtension').GetWhatsWrongCount());print([(n,f.GetTypeName2(),f.GetErrorCode2()) for n,f in mate_features(d).items() if f.GetErrorCode2()[0]])
