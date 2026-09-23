from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');print('cfg',typed(typed(d.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name)
for n,f in mate_features(d).items():
 if n.endswith('limits') or n.endswith('driver'):
  v=typed(f.GetDefinition(),'IAngleMateFeatureData');print(n,f.IsSuppressed(),f.GetTypeName2(),v.IsAdvancedMate,np.degrees([v.Angle,v.MinimumAngle,v.MaximumAngle]),typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension').DrivenState)
