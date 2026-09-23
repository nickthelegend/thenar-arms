"""Create a disposable CAD candidate from source-preserving seam partitions."""
from check_assembly_pose import *
s=attach();copies=[];evidence=[]
for k,name in enumerate(['Forearm_split_0','Forearm_lower_x_0','Forearm_lower_conditioned_healed']):
    path=ROOT/'solidworks/checkpoints'/(name+'.SLDPRT')
    d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0)
    p=typed(doc,'IPartDoc');b=typed(p.GetBodies2(0,False)[0],'IBody2');before=b.Check2()
    healed=None
    if before:healed=p.ImportDiagnosis(True,False,True,0)
    b=typed(p.GetBodies2(0,False)[0],'IBody2');row={'partition':k,'faults_before':before,'diagnosis_result':healed,'faults_after':b.Check2(),'volume_mm3':b.GetMassProperties(1)[3]*1e9,'box_m':list(b.GetBodyBox())}
    print(row,flush=True);evidence.append(row);copies.append(typed(b.Copy(),'IBody2'))
    assert row['faults_after']==0,row
doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0));p=typed(doc,'IPartDoc')
for k,b in enumerate(copies):
    f=p.CreateFeatureFromBody3(b,False,0);assert f is not None;typed(f,'IFeature').Name=f'Preserved_source_seam_partition_{k}'
fm=typed(doc.FeatureManager,'IFeatureManager');bs=p.GetBodies2(0,False)
f=fm.InsertCombineFeature(CONST.SWBODYADD,None,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,list(bs)))
if f is not None:typed(f,'IFeature').Name='Join_source_seam_partitions'
row={'partition_imports':evidence,'native_combine_created':f is not None,'bodies':[{'volume_mm3':typed(b,'IBody2').GetMassProperties(1)[3]*1e9,'kernel_faults':typed(b,'IBody2').Check2(),'box_m':list(typed(b,'IBody2').GetBodyBox())} for b in p.GetBodies2(0,False)]}
path=ROOT/'solidworks/checkpoints/Forearm_seam_reconstructed_candidate.SLDPRT';assert doc.SaveAs3(str(path),0,1)==0
(ROOT/'solidworks/evidence/Forearm_seam_reconstruction.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
