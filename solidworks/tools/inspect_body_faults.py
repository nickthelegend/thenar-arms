from native_hardware import *
import sys
s=attach();path=ROOT/sys.argv[1];d,e,w=s.OpenDoc6(str(path),1,1,'',0,0);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);p=typed(doc,'IPartDoc');rows=[]
for b in p.GetBodies2(0,False) or []:
    b=typed(b,'IBody2');fault=typed(b.Check3,'IFaultEntity')
    for k in range(fault.Count):
        ent=typed(fault.Entity2(k),'IEntity');kind=ent.GetType();row={'error':fault.ErrorCode(k),'entity_type':kind}
        try:
            if kind==CONST.swSelFACES:row['box_mm']=[v*1000 for v in typed(ent,'IFace2').GetBox()]
            elif kind==CONST.swSelEDGES:
                edge=typed(ent,'IEdge');row['endpoints_mm']=[[v*1000 for v in typed(vertex,'IVertex').GetPoint()] for vertex in [edge.GetStartVertex(),edge.GetEndVertex()] if vertex]
            elif kind==CONST.swSelVERTICES:row['point_mm']=[v*1000 for v in typed(ent,'IVertex').GetPoint()]
        except Exception as ex:row['inspection_error']=str(ex)
        rows.append(row)
out=ROOT/'solidworks/evidence'/(path.stem+'_fault_entities.json');out.write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
