"""Measure every leader component after native mate-driven motion."""
from build_leader_assembly import *
def main():
    s,doc,asm,cs=connect();m=manifest();w0=worlds(m);rows=[];jointpairs=[]
    for n in m['nodes']:
        if n['joint'] is None:continue
        dat=next(a for a in m['nodes'] if a['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith('_Encoder_L1'));c=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith('_Encoder_L1'));jointpairs.append((n,p,c))
    def refresh():
        nonlocal cs
        byname={typed(c,'IComponent2').Name2:typed(c,'IComponent2') for c in asm.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in json.loads(EVIDENCE.read_text())['components']}
    def measure(name,q):
        refresh();w=posed_worlds(m,q);actual={k:from_sw(c) for k,c in cs.items()};components=[];joints=[]
        for i in m['instances']:
            expected=w[i['node']]@matrix(i);a=actual[i['id']];components.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-expected[:3,3])),'angle_error_deg':float(np.rad2deg(Rotation.from_matrix(expected[:3,:3].T@a[:3,:3]).magnitude())),'measured_transform_mm':a.tolist()})
        for n,p,c in jointpairs:
            pt=actual[p['id']]@np.linalg.inv(w0[p['node']]@matrix(p))@w0[n['id']];ct=actual[c['id']]@np.linalg.inv(w0[c['node']]@matrix(c))@w0[n['id']];rel=np.linalg.inv(pt)@ct
            joints.append({'joint':n['joint']+1,'angle_deg':float(np.degrees(np.arctan2(rel[1,0],rel[0,0]))),'axis_origin_separation_mm':float(np.linalg.norm(rel[:3,3])),'axis_tilt_deg':float(np.degrees(np.arccos(np.clip(rel[2,2],-1,1))))})
        errors=[{'name':n,'error':f.GetErrorCode2()} for n,f in mate_features(doc).items() if f.GetErrorCode2()[0]!=0]
        row={'name':name,'command_deg':q,'components':components,'joints':joints,'mate_errors':errors,'max_position_error_mm':max(c['position_error_mm'] for c in components),'max_angle_error_deg':max(c['angle_error_deg'] for c in components)};row['kinematic_pass']=not errors and row['max_position_error_mm']<.001 and row['max_angle_error_deg']<.001
        print({k:v for k,v in row.items() if k not in ['components','joints']},flush=True);return row
    def setq(q):
        # Modify the real limit-angle definition for changed joints only.
        # A direct dimension trial changed a solver branch and was rejected.
        for j,angle in enumerate(q):
            f=mate_features(doc)[f'J{j+1}_Source_preview_limits'];data=typed(f.GetDefinition(),'IAngleMateFeatureData')
            value=math.radians(90+angle)
            if abs(data.Angle-value)>1e-10:data.Angle=value;assert f.ModifyDefinition(data,doc,None)
        doc.ForceRebuild3(False);doc.ClearUndoList()
    poses={'ZERO':[0]*6}
    for j,(lo,hi) in enumerate(m['limits']):
        for suffix,val in [('MIN',lo),('ZERO_AFTER_MIN',0),('MAX',hi),('ZERO_AFTER_MAX',0)]:q=[0]*6;q[j]=val;poses[f'J{j+1}_{suffix}']=q
    poses.update(HOME=[0,-25,35,0,0,20],MULTI=[20,-30,40,-20,30,25],ZERO_FINAL=[0]*6)
    out=ROOT/'solidworks/evidence/leader_joint_motion_measurements.json'
    for name,q in poses.items():setq(q);rows.append(measure(name,q));out.write_text(json.dumps(rows,indent=2));assert rows[-1]['kinematic_pass']
    fm=typed(doc.FeatureManager,'IFeatureManager');feature=asm.FeatureByName('Leader_Joint_Poses')
    if feature is None:
        data=typed(fm.CreateDefinition(CONST.swFmMateController),'IMateControllerFeatureData');feats=mate_features(doc);mates=[typed(feats[f'J{j+1}_Source_preview_limits'].GetSpecificFeature2(),'IMate2') for j in range(6)];data.Initialize(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,mates))
        useful={k:v for k,v in poses.items() if k in ['ZERO','HOME'] or k.endswith('_MIN') and 'AFTER' not in k or k.endswith('_MAX') and 'AFTER' not in k};useful['MID_RANGE']=[0,0,0,0,0,35]
        for name,q in useful.items():assert data.AddNewPosition(name);data.SetValues(name,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,np.deg2rad(np.array(q)+90).tolist()))
        feature=typed(fm.CreateFeature(data),'IFeature');feature.Name='Leader_Joint_Poses'
    configrows=[]
    for name,q in {'ZERO':[0]*6,'MID_RANGE':[0,0,0,0,0,35],'HOME':[0,-25,35,0,0,20]}.items():
        if name not in doc.GetConfigurationNames():assert doc.AddConfiguration3(name,'Source-defined pose','',0)
        doc.ShowConfiguration2(name)
        for j,angle in enumerate(q):
            f=mate_features(doc)[f'J{j+1}_Source_preview_limits'];dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');assert dim.SetSystemValue3(math.radians(90+angle),CONST.swSetValue_InSpecificConfigurations,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_BSTR,[name]))==0
        doc.ForceRebuild3(False);row=measure(name,q);configrows.append(row);assert row['kinematic_pass']
    (ROOT/'solidworks/evidence/leader_saved_configurations.json').write_text(json.dumps(configrows,indent=2))
    doc.ClearSelection2(True);v=typed(doc.ActiveView,'IModelView');z=np.array([1.,-1.,.8]);z/=np.linalg.norm(z);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);t=np.eye(4);t[:3,:3]=np.array([x,y,z]);v.Orientation3=sw_transform(s,t);doc.NameView('SOURCE_Z_UP');doc.ViewZoomtofit2();assert doc.SaveAs3(str(PATH),0,1)==0
    print('All 28 leader poses and 3 stored configurations passed.',flush=True)
if __name__=='__main__':main()
