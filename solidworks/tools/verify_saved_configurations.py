from probe_joint_motion import *
s,doc,asm,cs=connect();m=load_manifest();ev=[]
for name in ['ZERO','HOME','MID_RANGE']:
    if name not in doc.GetConfigurationNames():
        cfg=doc.GetConfigurationByName('Follower_Joint_Poses '+name)
        assert cfg is not None,name;typed(cfg,'IConfiguration').Name=name
for name,q in [('ZERO',[0]*6),('MID_RANGE',[0,0,0,0,0,35]),('HOME',[0,-25,35,0,0,20])]:
    doc.ShowConfiguration2(name)
    assert typed(typed(doc.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name==name,name
    doc.ForceRebuild3(False);w=posed_worlds(m,q);rows=[]
    evbuild=json.loads((ROOT/'solidworks/evidence/follower_assembly_build.json').read_text())
    byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)}
    cs={r['id']:byname[r['name2']] for r in evbuild['components']}
    for i in m['instances']:
        a=from_sw(cs[i['id']]);e=w[i['node']]@matrix(i)
        rows.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-e[:3,3])),'angle_error_deg':float(np.rad2deg(Rotation.from_matrix(e[:3,:3].T@a[:3,:3]).magnitude())),'actual_transform_mm':a.tolist()})
    errors=[(n,f.GetErrorCode2()) for n,f in mate_features(doc).items() if f.GetErrorCode2()[0]!=0]
    r={'configuration':name,'joint_degrees':q,'components':rows,'mate_errors':errors,'max_position_error_mm':max(x['position_error_mm'] for x in rows),'max_angle_error_deg':max(x['angle_error_deg'] for x in rows)}
    r['pass']=not errors and max(r['max_position_error_mm'],r['max_angle_error_deg'])<.001;ev.append(r)
    print({k:v for k,v in r.items() if k!='components'},flush=True)
(ROOT/'solidworks/evidence/saved_configuration_verification.json').write_text(json.dumps(ev,indent=2))
assert all(r['pass'] for r in ev)
doc.ClearSelection2(True);doc.ShowNamedView2('*Isometric',7);doc.ViewDisplayShaded();doc.ViewZoomtofit2();assert doc.SaveAs3(doc.GetPathName(),0,1)==0
