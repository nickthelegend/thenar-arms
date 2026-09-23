from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');s.CloseDoc(d.GetTitle());s,d,a,m,b,p=connect_robot('leader');f=typed(a.FeatureByName('Leader_Joint_Poses'),'IFeature');print('select after reopen',f.Select2(False,0));d.ClearSelection2(True)
