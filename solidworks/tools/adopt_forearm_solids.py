"""Replace only the failed surface feature; preserve established native joint datums."""
from check_assembly_pose import *
import shutil
s=attach();proof=json.loads((ROOT/'solidworks/evidence/Forearm_seam_comparison.json').read_text());assert proof['status'].startswith('ACCEPTED')
source=ROOT/'solidworks/checkpoints/Forearm_seam_reconstructed_candidate.SLDPRT'
d,e,w=s.OpenDoc6(str(source),1,1,'',0,0);sp=typed(model(d),'IPartDoc')
copies=[]
for b in sp.GetBodies2(0,False):
    b=typed(b,'IBody2');assert b.Check2()==0;copies.append(typed(b.Copy(),'IBody2'))
path=ROOT/'solidworks/parts/Forearm_MG996R_R3.SLDPRT'
backup=ROOT/'solidworks/checkpoints/pre_solid_forearm';backup.mkdir(exist_ok=True)
if not (backup/path.name).exists():shutil.copy2(path,backup/path.name)
d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);p=typed(doc,'IPartDoc')
assert not p.GetBodies2(0,False),'Already adopted'
f=typed(p.FeatureByName('Surface-Imported2'),'IFeature')
assert f.SetSuppression2(CONST.swSuppressFeature,CONST.swAllConfiguration,None)
for k,b in enumerate(copies):
    feat=p.CreateFeatureFromBody3(b,False,0);assert feat is not None;typed(feat,'IFeature').Name=f'R3_preserved_solid_partition_{k+1}'
doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,[.8,.25,.07,1,.5,.25,.1,0,0])
doc.ForceRebuild3(False);assert len(p.GetBodies2(0,False) or [])==3;assert not p.GetBodies2(1,False)
row={'path':str(path),'representation':'Three nonoverlapping solids in one rigid component; native union fails at source seam','surface_feature':'Suppressed checkpoint, retained for traceability','source_comparison':proof,'body_faults':[typed(b,'IBody2').Check2() for b in p.GetBodies2(0,False)]}
assert not any(row['body_faults']);assert doc.SaveAs3(str(path),0,1)==0
(ROOT/'solidworks/evidence/Forearm_adopted_solids.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
