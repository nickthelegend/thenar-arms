"""Export actual leader parts, then compare all source surfaces without redesign."""
from leader_parts import *
from export_part_mesh import main as export_mesh
import trimesh
def main():
    s=attach();m=manifest();out=ROOT/'solidworks/exports/leader_visual_mm';out.mkdir(exist_ok=True);rows=[]
    for part in m['parts']:
        name=part['id']
        if not name.endswith('_L1'):continue
        path=ROOT/('solidworks/parts/leader' if name.endswith('_Encoder_L1') else 'solidworks/hardware/leader')/(name+'.SLDPRT');dest=out/(name+'.stl');export_mesh(path,dest);s.CloseDoc(path.name)
    print('ALL_NATIVE_EXPORTS_COMPLETE; remaining work is independent mesh comparison',flush=True)
    for part in m['parts']:
        name=part['id']
        if not name.endswith('_L1'):continue
        source=ROOT/'robot-studio/public/models/so101'/part['file'];actual=out/(name+'.stl');a=trimesh.load(source);b=trimesh.load(actual);ev=json.loads((ROOT/'solidworks/evidence'/(name+'_leader_part.json')).read_text());native=ev.get('native_features',False)
        # Sectioned parts have their dedicated 50000-sample checks. Verify the
        # actual adopted files again using the same original exterior masks.
        mask=np.zeros(len(b.faces),dtype=bool)
        if name=='Base_Encoder_L1':mask=np.max(abs(b.triangles[:,:,0]+4),axis=1)<1e-4
        if name=='Forearm_Encoder_L1':mask=(np.max(abs(b.triangles[:,:,2]+23),axis=1)<1e-4)|((np.max(abs(b.triangles[:,:,0]),axis=1)<1e-4)&(np.max(b.triangles[:,:,2],axis=1)<-22.9999))|((np.max(abs(b.triangles[:,:,2]-16.2),axis=1)<1e-4)&(np.max(b.triangles[:,:,0],axis=1)<50.3341))
        exterior=b.submesh([np.flatnonzero(~mask)],append=True,repair=False) if any(mask) else b;errors=[]
        for x,y in [(a,b),(exterior,a)]:
            points=np.vstack([x.vertices,trimesh.sample.sample_surface(x,30000,seed=1015600)[0]]);dist=[]
            for k in range(0,len(points),100):dist.extend(trimesh.proximity.closest_point(y,points[k:k+100])[1])
            errors.append(float(max(dist)))
        volume=sum(x['volume_m3'] for x in ev['solids'])*1e9
        row={'part':name,'native_features':native,'source_volume_mm3':a.volume,'CAD_solid_volume_mm3':volume,'relative_volume_delta':volume/a.volume-1,'bounds_delta_mm':float(np.max(abs(b.bounds-a.bounds))),'bidirectional_surface_error_mm':errors,'comparison_tolerance_mm':.005,'strict_1_micron_surface_pass':max(errors)<.001,'surface_sheet_artifacts':ev.get('source_zero_thickness_sheets',[]),'surface_body_faults':ev.get('surface_body_faults',[])}
        row['pass']=bool(max(errors)<.005 and row['bounds_delta_mm']<.001 and abs(row['relative_volume_delta'])<(.001 if native else 1e-5))
        rows.append(row);(ROOT/'verification/leader_geometry_comparison.json').write_text(json.dumps(rows,indent=2));print(name,'PASS' if row['pass'] else 'FAIL','surface',max(errors),'volume',row['relative_volume_delta'],flush=True)
    assert all(r['pass'] for r in rows)
if __name__=='__main__':main()
