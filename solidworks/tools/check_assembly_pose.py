from mate_follower import *
from scipy.spatial.transform import Rotation

def from_sw(c):
    a=np.array(typed(c.Transform2,'IMathTransform').ArrayData)
    t=np.eye(4);t[:3,:3]=a[:9].reshape(3,3).T;t[:3,3]=a[9:12]*1000
    return t

def connect():
    s=attach();p=ROOT/'solidworks/assemblies/SO101_Follower_Reconstruction_WIP.SLDASM'
    d,e,w=s.OpenDoc6(str(p),2,1,'',0,0);assert d is not None,(e,w)
    doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc')
    ev=json.loads((ROOT/'solidworks/evidence/follower_assembly_build.json').read_text())
    byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)}
    return s,doc,asm,{r['id']:byname[r['name2']] for r in ev['components']}

def main():
    s,doc,asm,cs=connect();m=load_manifest();w=worlds(m);rows=[]
    for i in m['instances']:
        expected=w[i['node']]@matrix(i);actual=from_sw(cs[i['id']])
        rows.append({'id':i['id'],'fixed':bool(cs[i['id']].IsFixed()),'position_error_mm':float(np.linalg.norm(actual[:3,3]-expected[:3,3])),'angle_error_deg':float(np.rad2deg(Rotation.from_matrix(expected[:3,:3].T@actual[:3,:3]).magnitude())),'actual_transform_mm':actual.tolist()})
    (ROOT/'solidworks/evidence/zero_pose_after_mating.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k!='actual_transform_mm'} for r in rows],indent=2))
    for name,f in mate_features(doc).items():
        if 'limits' in name:
            md=typed(f.GetDefinition(),'IAngleMateFeatureData')
            print(name,{p:getattr(md,p,'N/A') for p in ['Angle','MaximumAngle','MinimumAngle','IsAdvancedMate','MateAlignment','FlipDimension']},flush=True)
if __name__=='__main__':main()
