from real_limit_mates import *
s,d,a,m,b,p=connect_robot('leader');fs=mate_features(d);f=fs['J1_Source_preview_limits'];v=typed(f.GetDefinition(),'IAngleMateFeatureData');v.ReferenceEntity=com.VARIANT(pythoncom.VT_DISPATCH,None);print('modify',f.ModifyDefinition(v,d,None));d.EditRebuild3();d.ForceRebuild3(False);cs={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};print('status without reference',cs['Shoulder_Encoder_L1-1'].GetConstrainedStatus());v=typed(f.GetDefinition(),'IAngleMateFeatureData');print('ref',v.ReferenceEntity)

