from build_leader_assembly import *
s,d,a,c=connect();m=manifest();i=next(i for i in m['instances'] if i['part']=='Shoulder_Encoder_L1');rows=[]
for angle in [15,100,0]:
    q=[angle,-25,35,0,0,20];w=posed_worlds(m,q);drag=typed(a.GetDragOperator(),'IDragOperator');assert drag.AddComponent(c[i['id']],False);drag.TransformType=2;drag.DragMode=2;drag.UseAbsoluteTransform=True;drag.ApplyToThisConfiguration=True;assert drag.BeginDrag();ok=drag.Drag(sw_transform(s,w[i['node']]@matrix(i)));corrected=drag.DragCorrected;drag.EndDrag();d.ForceRebuild3(False);d.ClearUndoList();errors=[]
    for x in m['instances']:
        actual=from_sw(c[x['id']]);expected=w[x['node']]@matrix(x);errors.append((np.linalg.norm(actual[:3,3]-expected[:3,3]),np.rad2deg(Rotation.from_matrix(expected[:3,:3].T@actual[:3,:3]).magnitude())))
    f=mate_features(d)['J1_Source_preview_limits'];v=typed(f.GetDefinition(),'IAngleMateFeatureData');row={'requested_q1':angle,'drag_result':ok,'corrected':corrected,'angle_property_deg':np.degrees(v.Angle)-90,'limits':np.degrees([v.MinimumAngle,v.MaximumAngle]).tolist(),'advanced':v.IsAdvancedMate,'max_position_difference_from_requested_mm':float(max(x[0] for x in errors)),'max_angle_difference_from_requested_deg':float(max(x[1] for x in errors)),'mate_errors':[(n,f.GetErrorCode2()) for n,f in mate_features(d).items() if f.GetErrorCode2()[0]!=0]};rows.append(row);print(row,flush=True)
(ROOT/'solidworks/evidence/leader_limit_drag_probe.json').write_text(json.dumps(rows,indent=2))
