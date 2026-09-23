from check_assembly_pose import *
s=attach();rows=[]
for path in list((ROOT/'solidworks/parts').glob('*.SLDPRT'))+list((ROOT/'solidworks/hardware').glob('*.SLDPRT')):
    if path.name.startswith('~$'):continue
    d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);assert d is not None,(path,e);doc=model(d);p=typed(doc,'IPartDoc')
    row={'path':str(path),'part':path.stem,'bodies':[],'surface_count':len(p.GetBodies2(1,False) or [])}
    for b in p.GetBodies2(0,False) or []:
        b=typed(b,'IBody2');row['bodies'].append({'kernel_faults':b.Check2(),'volume_mm3':b.GetMassProperties(1)[3]*1e9,'bounds_m':list(b.GetBodyBox())})
    print(row['part'],[(b['kernel_faults'],b['volume_mm3']) for b in row['bodies']],'surfaces',row['surface_count'],flush=True);rows.append(row)
(ROOT/'solidworks/evidence/all_part_body_checks.json').write_text(json.dumps(rows,indent=2))
