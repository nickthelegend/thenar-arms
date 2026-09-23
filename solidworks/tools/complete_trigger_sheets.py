from preserve_source_sheets import *
from export_part_mesh import main as export_mesh
path=ROOT/'solidworks/parts/leader/Trigger_Encoder_L1.SLDPRT';temp=ROOT/'solidworks/checkpoints/import_transport/Trigger_actual_solid.stl';export_mesh(path,temp)
s=attach();d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);p=typed(doc,'IPartDoc');assert not p.GetBodies2(1,False)
a=trimesh.load(ROOT/'so101-mg996r/output/encoder-leader-l1/print-parts/Trigger_Encoder_L1.stl');b=trimesh.load(temp);sheets=add_sheets(doc,a,b,6);assert len(sheets)==3;faults=[typed(b,'IBody2').Check2() for b in p.GetBodies2(1,False)];assert not any(faults);assert doc.SaveAs3(str(path),0,1)==0
evpath=ROOT/'solidworks/evidence/Trigger_Encoder_L1_leader_part.json';ev=json.loads(evpath.read_text());ev.update(source_zero_thickness_sheets=sheets,surface_bodies=len(faults),surface_body_faults=faults);evpath.write_text(json.dumps(ev,indent=2));print('Trigger: preserved 3 source surface patches, all kernel checks zero',flush=True)
