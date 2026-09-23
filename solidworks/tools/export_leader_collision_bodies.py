"""Export each real leader CAD solid independently; retain sheets only in visuals."""
from leader_parts import *
from export_part_mesh import main as export_mesh
import trimesh

def main():
    s=attach();out=ROOT/'verification/leader_collision_check_meshes';out.mkdir(exist_ok=True)
    checkpoint=ROOT/'solidworks/checkpoints/leader_collision_bodies';checkpoint.mkdir(exist_ok=True);rows=[]
    for item in manifest()['parts']:
        name=item['id']
        if not name.endswith('_L1'):continue
        path=ROOT/('solidworks/parts/leader' if name.endswith('_Encoder_L1') else 'solidworks/hardware/leader')/(name+'.SLDPRT')
        d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);assert d is not None,(e,w);part=typed(model(d),'IPartDoc');copies=[]
        for raw in part.GetBodies2(0,False) or []:
            b=typed(raw,'IBody2');assert b.Check2()==0;copies.append((typed(b.Copy(),'IBody2'),b.GetMassProperties(1)[3]*1e9))
        assert copies,name
        for k,(body,volume) in enumerate(copies):
            native=checkpoint/(name+f'_body{k}.SLDPRT');rawstl=checkpoint/(name+f'_body{k}.stl');dest=out/(name+f'_body{k}.stl')
            doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0))
            assert typed(doc,'IPartDoc').CreateFeatureFromBody3(body,False,0) is not None
            assert doc.SaveAs3(str(native),0,1)==0;export_mesh(native,rawstl);s.CloseDoc(doc.GetTitle())
            mesh=trimesh.load(rawstl);mesh.merge_vertices(digits_vertex=5);mesh.update_faces(mesh.nondegenerate_faces(height=1e-8));mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
            r={'part':name,'body':k,'path':str(dest),'CAD_volume_mm3':volume,'mesh_volume_mm3':float(mesh.volume),'relative_volume_error':float(mesh.volume/volume-1),'positive_volume':bool(mesh.is_volume),'weld_decimal_places_mm':5}
            rows.append(r);(ROOT/'verification/leader_collision_mesh_preparation.json').write_text(json.dumps(rows,indent=2));print(r,flush=True)
            assert r['positive_volume'] and abs(r['relative_volume_error'])<.001,r
            mesh.export(dest,file_type='stl_ascii')
        s.CloseDoc(path.name)
    print('Prepared',len(rows),'CAD solid-body collision meshes; zero-thickness sheets excluded from volumetric intersection only.')
if __name__=='__main__':main()
