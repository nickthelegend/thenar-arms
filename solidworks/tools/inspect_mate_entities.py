from check_assembly_pose import *
s,doc,asm,cs=connect()
for name,f in mate_features(doc).items():
    if 'Rigid' not in name:continue
    mate=typed(f.GetSpecificFeature2(),'IMate2')
    rows=[]
    for k in range(mate.GetMateEntityCount()):
        e=typed(mate.MateEntity(k),'IMateEntity2')
        rows.append({'component':typed(e.ReferenceComponent,'IComponent2').Name2,'type':e.ReferenceType})
    print(name,rows,flush=True)
