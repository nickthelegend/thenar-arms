"""Exercise the real SW mate solver; record measured component poses, never just targets."""
from probe_joint_motion import *
import csv

def drag_to(s,asm,c,t):
    d=typed(asm.GetDragOperator(),'IDragOperator');assert d.AddComponent(c,False)
    d.TransformType=2;d.UseAbsoluteTransform=True;d.ApplyToThisConfiguration=True
    d.CollisionDetectionEnabled=False;d.DynamicClearanceEnabled=False
    assert d.BeginDrag()
    try:return bool(d.Drag(sw_transform(s,t)))
    finally:d.EndDrag()

def main():
    s,doc,asm,cs=connect();m=load_manifest();w0=worlds(m)
    joints=[]
    for n in m['nodes']:
        if n['joint'] is None:continue
        datum=next(a for a in m['nodes'] if a['id']==n['parent'])
        parent=next(i for i in m['instances'] if i['node']==datum['parent'] and i['part'].endswith('_MG996R_R3'))
        child=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith('_MG996R_R3'))
        joints.append((n,parent,child))
    def measure(q):
        w=posed_worlds(m,q);actual={key:from_sw(c) for key,c in cs.items()};rows=[]
        for i in m['instances']:
            e=w[i['node']]@matrix(i);a=actual[i['id']]
            rows.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-e[:3,3])),'angle_error_deg':float(np.rad2deg(Rotation.from_matrix(e[:3,:3].T@a[:3,:3]).magnitude())),'measured_transform_mm':a.tolist()})
        jr=[]
        for n,p,c in joints:
            pt=actual[p['id']]@np.linalg.inv(w0[p['node']]@matrix(p))@w0[n['id']]
            ct=actual[c['id']]@np.linalg.inv(w0[c['node']]@matrix(c))@w0[n['id']]
            rel=np.linalg.inv(pt)@ct
            jr.append({'joint':n['joint']+1,'measured_angle_deg':float(np.degrees(np.arctan2(rel[1,0],rel[0,0]))),'axis_origin_separation_mm':float(np.linalg.norm(rel[:3,3])),'axis_tilt_deg':float(np.degrees(np.arccos(np.clip(rel[2,2],-1,1))))})
        return rows,jr
    def pose(name,q):
        old=next((r for r in evidence if r['name']==name),None)
        if old:return old
        results=[]
        for j in range(6):
            f=mate_features(doc)[f'J{j+1}_Source_preview_limits']
            md=typed(f.GetDefinition(),'IAngleMateFeatureData');value=math.radians(90+q[j])
            if abs(md.Angle-value)<1e-10:results.append(True);continue
            md.Angle=value;results.append(bool(f.ModifyDefinition(md,doc,None)))
        doc.ForceRebuild3(False)
        rows,jr=measure(q);errors=[{'name':n,'error':f.GetErrorCode2()} for n,f in mate_features(doc).items() if f.GetErrorCode2()[0]!=0]
        row={'name':name,'command_deg':q.copy(),'method':'Native limit-angle mate current-angle modification followed by rebuild','mate_modify_results':results,'components':rows,'joints':jr,'mate_errors':errors,'max_position_error_mm':max(a['position_error_mm'] for a in rows),'max_angle_error_deg':max(a['angle_error_deg'] for a in rows)}
        row['kinematic_pass']=all(results) and not errors and row['max_position_error_mm']<.001 and row['max_angle_error_deg']<.001
        print({k:v for k,v in row.items() if k not in ['components','joints']},flush=True)
        evidence.append(row);out.write_text(json.dumps(evidence,indent=2))
        return row
    out=ROOT/'solidworks/evidence/joint_motion_measurements.json';evidence=json.loads(out.read_text()) if out.exists() else []
    pose('ZERO',[0]*6)
    for j in range(6):
        for name,value in [('MIN',m['limits'][j][0]),('ZERO_AFTER_MIN',0),('MAX',m['limits'][j][1]),('ZERO_AFTER_MAX',0)]:
            q=[0]*6;q[j]=value;pose(f'J{j+1}_{name}',q)
    pose('HOME',[0,-25,35,0,0,20]);pose('MULTI',[20,-30,40,-20,30,25]);pose('ZERO_FINAL',[0]*6)
    doc.ClearSelection2(True);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2();assert doc.SaveAs3(doc.GetPathName(),0,1)==0
    fields=['Joint','Parent','Child','Axis','Minimum','Maximum','Zero','Movement PASS/FAIL','Axis PASS/FAIL','Collision result','Mate result','Evidence','Notes']
    with (ROOT/'verification/joint_verification.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for n,p,c in joints:
            j=n['joint'];tests=[r for r in evidence if r['name'].startswith(f'J{j+1}_')]
            axisok=all(x['axis_origin_separation_mm']<.001 and x['axis_tilt_deg']<.001 for r in tests for x in r['joints'])
            writer.writerow(dict(zip(fields,[f'J{j+1}',p['part'],c['part'],'local +Z',*m['limits'][j],0,'PASS' if all(r['kinematic_pass'] for r in tests) else 'FAIL','PASS' if axisok else 'FAIL','NOT CHECKED; forearm is surface-only','PASS' if all(not r['mate_errors'] for r in tests) else 'FAIL',str(out.relative_to(ROOT)),'Preview limits only; physical validation and collision sweep pending'])))
if __name__=='__main__':main()
