from probe_joint_motion import *
s,doc,asm,cs=connect();m=load_manifest();q=[0,-25,35,0,0,20]
assert typed(typed(doc.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name=='HOME'
assert doc.SaveAs3(doc.GetPathName(),0,1)==0
w=posed_worlds(m,q);joint=next(n for n in m['nodes'] if n['joint']==0);i=next(i for i in m['instances'] if i['part']=='Shoulder_MG996R_R3')
r=np.eye(4);r[:3,:3]=Rotation.from_euler('z',10,degrees=True).as_matrix();delta=w[joint['id']]@r@np.linalg.inv(w[joint['id']])
doc.ClearSelection2(True);assert cs[i['id']].Select4(False,None,False)
drag=typed(asm.GetDragOperator(),'IDragOperator');assert drag.AddComponent(cs[i['id']],False)
drag.TransformType=2;drag.DragMode=0;drag.UseAbsoluteTransform=True;drag.CollisionDetectionEnabled=False;drag.DynamicClearanceEnabled=False
assert drag.BeginDrag()
try:
    q[0]=10;result=drag.Drag(sw_transform(s,posed_worlds(m,q)[i['node']]@matrix(i)))
finally:drag.EndDrag()
q[0]=10;expected=posed_worlds(m,q);rows=[]
for i in m['instances']:
    a=from_sw(cs[i['id']]);e=expected[i['node']]@matrix(i)
    rows.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-e[:3,3])),'angle_error_deg':float(np.rad2deg(Rotation.from_matrix(e[:3,:3].T@a[:3,:3]).magnitude()))})
evidence={'drag_as_ui_result':bool(result),'source_joint_degrees':q,'components':rows,'max_position_error_mm':max(r['position_error_mm'] for r in rows),'max_angle_error_deg':max(r['angle_error_deg'] for r in rows)}
(ROOT/'solidworks/evidence/manual_drag_probe.json').write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence),flush=True)
# Reload the saved HOME configuration; discard this isolated unsaved drag probe.
path=doc.GetPathName();s.CloseDoc(doc.GetTitle());d,e,w=s.OpenDoc6(path,2,1,'HOME',0,0);assert d is not None,(e,w)
