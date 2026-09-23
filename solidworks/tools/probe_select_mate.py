from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');fs=mate_features(d);f=fs['J1_Source_preview_limits'];print(f.GetTypeName2(),f.Select2(False,0));print('suppress',f.SetSuppression2(CONST.swSuppressFeature,CONST.swAllConfiguration,None));d.ClearSelection2(True)
