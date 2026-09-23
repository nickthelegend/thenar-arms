from build_leader_assembly import *
s,d,a,c=connect();m=manifest();w0=worlds(m)
def angles():
    global c
    byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in a.GetComponents(False)};c={r['id']:byname[r['name2']] for r in json.loads(EVIDENCE.read_text())['components']}
    actual={k:from_sw(v) for k,v in c.items()};rows=[]
    for n in m['nodes']:
        if n['joint'] is None:continue
        dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith('_Encoder_L1'));child=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith('_Encoder_L1'));pt=actual[p['id']]@np.linalg.inv(w0[p['node']]@matrix(p))@w0[n['id']];ct=actual[child['id']]@np.linalg.inv(w0[child['node']]@matrix(child))@w0[n['id']];rel=np.linalg.inv(pt)@ct;rows.append({'joint':n['joint']+1,'q':float(np.degrees(np.arctan2(rel[1,0],rel[0,0]))),'separation_mm':float(np.linalg.norm(rel[:3,3]))})
    return rows
print('Before',angles(),flush=True)
n=next(n for n in m['nodes'] if n['joint']==0);i=next(i for i in m['instances'] if i['part']=='Shoulder_Encoder_L1');mu=typed(s.GetMathUtility(),'IMathUtility');pt=mu.CreatePoint(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,(w0[n['id']][:3,3]/1000).tolist()));axis=mu.CreateVector(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,w0[n['id']][:3,2].tolist()));delta=mu.CreateTransformRotateAxis(pt,axis,math.radians(5))
op=typed(a.GetDragOperator(),'IDragOperator');op.AddComponent(c[i['id']],False);op.TransformType=1;op.DragMode=2;op.IsRelaxationEval=True;op.UseAbsoluteTransform=False;op.ApplyToThisConfiguration=True;print('Begin',op.BeginDrag());print('Move',op.DragAsUI(delta));print('End',op.EndDrag());print('Immediately',angles(),flush=True);d.ForceRebuild3(False);d.ClearUndoList();print('After',angles(),flush=True)

