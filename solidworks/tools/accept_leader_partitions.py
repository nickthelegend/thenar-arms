"""Accept sectioned CAD only after kernel, volume, bounds and exterior checks."""
from native_hardware import *
from export_part_mesh import main as export_mesh
import numpy as np,trimesh,sys
from preserve_source_sheets import add_sheets
def distances(mesh,points):return np.concatenate([trimesh.proximity.closest_point(mesh,points[k:k+100])[1] for k in range(0,len(points),100)])
def main(name):
    sources={'Base_Encoder_L1':['Leader_base_x0','Leader_base_x1'],'Trigger_Encoder_L1':['Leader_trigger_z1'],'Forearm_Encoder_L1':['Leader_forearm_upper_conditioned','Leader_forearm_upper_z1','Leader_forearm_lower_right','Leader_forearm_lower_left']}[name]
    s=attach();s.CloseDoc(name+'_partition_candidate.SLDPRT');copies=[]
    for src in sources:
        path=ROOT/'solidworks/checkpoints'/(src+'.SLDPRT');d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);part=typed(model(d),'IPartDoc');assert not part.GetBodies2(1,False),src
        for b in part.GetBodies2(0,False) or []:
            b=typed(b,'IBody2');assert b.Check2()==0 and b.GetMassProperties(1)[3]>1e-15,(src,b.Check2());copies.append(typed(b.Copy(),'IBody2'))
    assert copies
    doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0));part=typed(doc,'IPartDoc')
    for k,b in enumerate(copies):typed(part.CreateFeatureFromBody3(b,False,0),'IFeature').Name=f'Preserved_partition_{k+1}'
    candidate=ROOT/'solidworks/checkpoints'/(name+'_partition_candidate.SLDPRT');assert doc.SaveAs3(str(candidate),0,1)==0
    stl=ROOT/'solidworks/checkpoints/import_transport'/(name+'_partition_CAD.stl');export_mesh(candidate,stl)
    original=trimesh.load(ROOT/'so101-mg996r/output/encoder-leader-l1/print-parts'/(name+'.stl'));actual=trimesh.load(stl);pure_solid_mesh=actual.copy();sheets=[]
    if name.startswith(('Trigger','Forearm')):
        s.ActivateDoc3(doc.GetTitle(),False,0,0);sheets=add_sheets(doc,original,actual,6 if name.startswith('Trigger') else 16.2);assert doc.SaveAs3(str(candidate),0,1)==0;export_mesh(candidate,stl);actual=trimesh.load(stl)
    mask=np.zeros(len(actual.faces),dtype=bool)
    if name.startswith('Base'):mask=np.max(abs(actual.triangles[:,:,0]+4),axis=1)<1e-4
    if name.startswith('Forearm'):mask=(np.max(abs(actual.triangles[:,:,2]+23),axis=1)<1e-4)|((np.max(abs(actual.triangles[:,:,0]),axis=1)<1e-4)&(np.max(actual.triangles[:,:,2],axis=1)<-22.9999))|((np.max(abs(actual.triangles[:,:,2]-16.2),axis=1)<1e-4)&(np.max(actual.triangles[:,:,0],axis=1)<50.3341))
    exterior=actual.submesh([np.flatnonzero(~mask)],append=True,repair=False);errors=[]
    for a,b in [(original,actual),(exterior,original)]:
        points=np.vstack([a.vertices,trimesh.sample.sample_surface(a,50000,seed=1015600)[0]]);errors.append(float(max(distances(b,points))))
    row={'part':name,'candidate':str(candidate),'CAD_bodies':len(copies),'source_volume_mm3':original.volume,'CAD_volume_mm3':actual.volume,'relative_volume_delta':float(actual.volume/original.volume-1),'bounds_delta_mm':float(np.max(abs(actual.bounds-original.bounds))),'bidirectional_exterior_error_mm':errors,'excluded_internal_partition_triangles':int(mask.sum()),'status':'PENDING','method':'All source vertices plus 50000 samples compared to CAD; reverse uses exterior excluding only internal cut planes. Original unchanged.'}
    if name.startswith('Forearm'):row['numerical_conditioning']='Upper region starts at Z=16.20001 rather than 16.2 mm to remove coincident source facets rejected by the CAD kernel; 0.00001 mm internal gap, approximately 0.0238 mm3 removed. This is a disclosed numerical tolerance repair, not mathematical identity.'
    row['source_zero_thickness_sheets']=sheets
    ok=abs(row['relative_volume_delta'])<1e-5 and row['bounds_delta_mm']<.001 and max(errors)<.001;row['status']='ACCEPTED' if ok else 'REJECTED';proof=ROOT/'solidworks/evidence'/(name+'_partition_comparison.json');proof.write_text(json.dumps(row,indent=2));print(json.dumps(row,indent=2),flush=True);assert ok
    target=ROOT/'solidworks/parts/leader'/(name+'.SLDPRT');backup=ROOT/'solidworks/checkpoints/leader_failed_imports';backup.mkdir(exist_ok=True)
    if not (backup/target.name).exists():shutil.copy2(target,backup/target.name)
    d,e,w=s.OpenDoc6(str(target),1,1,'',0,0);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);part=typed(doc,'IPartDoc');f=doc.FirstFeature();old=[]
    while f:
        f=typed(f,'IFeature')
        if f.Name.startswith(('Imported','Surface-Imported')):old.append(f)
        f=f.GetNextFeature()
    assert old
    for f in old:assert f.SetSuppression2(CONST.swSuppressFeature,CONST.swAllConfiguration,None)
    assert not part.GetBodies2(0,False) and not part.GetBodies2(1,False)
    d,e,w=s.OpenDoc6(str(candidate),1,1,'',0,0);sourcepart=typed(model(d),'IPartDoc')
    for k,b in enumerate(sourcepart.GetBodies2(0,False)):
        b=typed(b,'IBody2');feat=part.CreateFeatureFromBody3(b.Copy(),False,0);assert feat is not None;typed(feat,'IFeature').Name=f'L1_preserved_solid_partition_{k+1}'
    if sheets:
        s.ActivateDoc3(doc.GetTitle(),False,0,0);add_sheets(doc,original,pure_solid_mesh,6 if name.startswith('Trigger') else 16.2)
    doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,[.12,.40,.55,1,.5,.25,.1,0,0]);doc.ForceRebuild3(False)
    bodies=part.GetBodies2(0,False);assert bodies and all(typed(b,'IBody2').Check2()==0 for b in bodies);assert doc.SaveAs3(str(target),0,1)==0
    evpath=ROOT/'solidworks/evidence'/(name+'_leader_part.json');ev=json.loads(evpath.read_text());ev.update(geometry='Source-preserving sectioned solid geometry with native joint datums; original failed import suppressed',partition_comparison=str(proof),source_zero_thickness_sheets=sheets,surface_body_faults=[typed(b,'IBody2').Check2() for b in part.GetBodies2(1,False) or []],surface_bodies=len(part.GetBodies2(1,False) or []),solids=[{'kernel_faults':typed(b,'IBody2').Check2(),'box_m':list(typed(b,'IBody2').GetBodyBox()),'volume_m3':typed(b,'IBody2').GetMassProperties(1)[3]} for b in bodies]);evpath.write_text(json.dumps(ev,indent=2));print('Adopted',name,len(bodies),'valid bodies',flush=True)
if __name__=='__main__':main(sys.argv[1])
