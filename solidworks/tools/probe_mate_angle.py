from check_assembly_pose import *
from probe_joint_motion import posed_worlds
s=attach();path=ROOT/'solidworks/assemblies/SO101_Follower_Reconstruction_WIP.SLDASM'
s.CloseDoc(str(path))
s,doc,asm,cs=connect();m=load_manifest()
f=mate_features(doc)['J1_Source_preview_limits'];md=typed(f.GetDefinition(),'IAngleMateFeatureData')
md.Angle=math.radians(105)
print('modify',f.ModifyDefinition(md,doc,None),flush=True);doc.ForceRebuild3(False)
q=[15,0,0,0,0,0];w=posed_worlds(m,q)
for i in m['instances']:
    a=from_sw(cs[i['id']]);e=w[i['node']]@matrix(i)
    print(i['id'],np.linalg.norm(a[:3,3]-e[:3,3]),np.rad2deg(Rotation.from_matrix(e[:3,:3].T@a[:3,:3]).magnitude()),flush=True)
md=typed(f.GetDefinition(),'IAngleMateFeatureData');md.Angle=math.pi/2
print('restore',f.ModifyDefinition(md,doc,None),flush=True);doc.ForceRebuild3(False)
