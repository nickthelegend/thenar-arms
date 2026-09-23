"""Unit-density geometric properties; never label these as actual robot inertias."""
from check_assembly_pose import *
import yaml
s=attach();parts=[];checks=[]
for entry in json.loads((ROOT/'solidworks/evidence/all_part_body_checks.json').read_text()):
    d,e,w=s.OpenDoc6(entry['path'],1,1,'',0,0);p=typed(model(d),'IPartDoc');bodies=[]
    for b in p.GetBodies2(0,False):
        b=typed(b,'IBody2');mp=np.array(b.GetMassProperties(1));copy=typed(b.Copy(),'IBody2');t=np.eye(4);t[:3,3]=[1000,2000,3000];copy.ApplyTransform(sw_transform(s,t));shift=np.array(copy.GetMassProperties(1))
        checks.append({'part':entry['part'],'centroid_translation_error_m':float(np.max(abs(shift[:3]-mp[:3]-[1,2,3]))),'central_moment_translation_delta':float(np.max(abs(shift[6:]-mp[6:])))})
        bodies.append({'centroid_uniform_density_m':mp[:3].tolist(),'volume_m3':float(mp[3]),'surface_area_m2':float(mp[4]),'calculation_density_kg_m3':1,'raw_mass_properties_SI_density_1':mp.tolist()})
    parts.append({'part':entry['part'],'status':'CAD MEASURED geometric integrals only; physical mass/COM/inertia UNVERIFIED','physical_mass_kg':None,'physical_com_m':None,'physical_inertia_kg_m2':None,'bodies':bodies})
out={'status':'Geometry prepared; physical dynamics incomplete. Unit-density integrals are not assigned material densities.','manufacturer_reference':{'component':'Genuine TowerPro MG996R','mass_kg':.055,'source':'https://towerpro.com.tw/product/mg996r/','applicability_to_users_generic_units':'UNVERIFIED','COM_and_inertia':'UNVERIFIED'},'printed_material':{'source':'R3-PRINT.md and plate-report.json','type':'Generic PETG','infill':'25% gyroid, 4 walls','plate_filament_total_g':496.88,'includes':'Supports and brim; cannot distribute this total among rigid links','physical_mass_COM_inertia':'UNVERIFIED'},'part_geometry':parts,'translation_invariance_checks':checks}
(ROOT/'simulation/inertial_properties.yaml').write_text(yaml.safe_dump(out,sort_keys=False))
print(json.dumps({'parts':len(parts),'max_centroid_check_error_m':max(c['centroid_translation_error_m'] for c in checks),'max_moment_translation_delta':max(c['central_moment_translation_delta'] for c in checks)}),flush=True)
