from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');d.ShowConfiguration2('HOME');d.ForceRebuild3(False);r=measure(d,a,m,b,'HOME_DEBUG',[0,-25,35,0,0,20]);print(r['joints']);fs=mate_features(d)
for name in ['J5_Source_preview_limits','J5_Pose_driver']:
 v=typed(fs[name].GetDefinition(),'IAngleMateFeatureData');print(name,v.Angle,v.MateAlignment,v.FlipDimension,v.ReferenceEntity)
