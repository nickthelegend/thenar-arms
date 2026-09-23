"""Range-preserving native angle updates and direct native limit readback."""
from build_leader_assembly import *
from prepare_follower_parts import load_manifest
import sys,shutil

def connect_robot(robot):
    path=ROOT/f'solidworks/assemblies/SO101_{robot.title()}_Master.SLDASM';s=attach();d,e,w=s.OpenDoc6(str(path),2,1,'',0,0);assert d is not None,(e,w);doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0);asm=typed(doc,'IAssemblyDoc');m=manifest() if robot=='leader' else load_manifest();build=json.loads((ROOT/f'solidworks/evidence/{robot}_assembly_build.json').read_text());return s,doc,asm,m,build,path

def set_pose(doc,features,q,limits,free=True,force=False):
    config=typed(typed(doc.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name
    for j in range(6):
        f=features[f'J{j+1}_Source_preview_limits']
        if f.IsSuppressed():assert f.SetSuppression2(CONST.swUnSuppressFeature,CONST.swThisConfiguration,None)
    for j,angle in enumerate(q):
        assert limits[j][0]-1e-8 <= angle <= limits[j][1]+1e-8
        f=features[f'J{j+1}_Pose_driver']
        if f.IsSuppressed():assert f.SetSuppression2(CONST.swUnSuppressFeature,CONST.swThisConfiguration,None)
        dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension')
        assert dim.SetSystemValue3(math.radians(90+angle),CONST.swSetValue_InSpecificConfigurations,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_BSTR,[config]))==0
    doc.ForceRebuild3(False)
    for j in range(6):
        f=features[f'J{j+1}_Pose_driver' if free else f'J{j+1}_Source_preview_limits']
        if not f.IsSuppressed():assert f.SetSuppression2(CONST.swSuppressFeature,CONST.swThisConfiguration,None)
    doc.ForceRebuild3(False);doc.ClearUndoList()

def measure(doc,asm,m,build,name,q):
    byname={typed(x,'IComponent2').Name2:typed(x,'IComponent2') for x in asm.GetComponents(False)};cs={r['id']:byname[r['name2']] for r in build['components']};w=posed_worlds(m,q);rows=[];limits=[]
    for i in m['instances']:
        a=from_sw(cs[i['id']]);b=w[i['node']]@matrix(i);rows.append({'id':i['id'],'position_error_mm':float(np.linalg.norm(a[:3,3]-b[:3,3])),'angle_error_deg':float(np.degrees(Rotation.from_matrix(b[:3,:3].T@a[:3,:3]).magnitude())),'measured_transform_mm':a.tolist()})
    fs=mate_features(doc);errors=[(n,f.GetErrorCode2()) for n,f in fs.items() if f.GetErrorCode2()[0]!=0]
    for j,(lo,hi) in enumerate(m['limits']):
        f=fs[f'J{j+1}_Source_preview_limits'];v=typed(f.GetDefinition(),'IAngleMateFeatureData');dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension');r={'joint':j+1,'active':not f.IsSuppressed(),'advanced':bool(v.IsAdvancedMate),'minimum_degrees':float(np.degrees(v.MinimumAngle)-90),'maximum_degrees':float(np.degrees(v.MaximumAngle)-90),'current_dimension_driven_state':dim.DrivenState};r['pass']=r['advanced'] and abs(r['minimum_degrees']-lo)<1e-6 and abs(r['maximum_degrees']-hi)<1e-6 and f.GetTypeName2()=='MateLimitPlanarAngleDim' and r['current_dimension_driven_state']==CONST.swDimensionDriving;limits.append(r)
    actual={r['id']:np.array(r['measured_transform_mm']) for r in rows};w0=worlds(m);joints=[];suffix='_Encoder_L1' if any(i['part'].endswith('_Encoder_L1') for i in m['instances']) else '_MG996R_R3'
    for n in m['nodes']:
        if n['joint'] is None:continue
        dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith(suffix));c=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith(suffix));pt=actual[p['id']]@np.linalg.inv(w0[p['node']]@matrix(p))@w0[n['id']];ct=actual[c['id']]@np.linalg.inv(w0[c['node']]@matrix(c))@w0[n['id']];rel=np.linalg.inv(pt)@ct;joints.append({'joint':n['joint']+1,'angle_deg':float(np.degrees(np.arctan2(rel[1,0],rel[0,0]))),'axis_origin_separation_mm':float(np.linalg.norm(rel[:3,3])),'axis_tilt_deg':float(np.degrees(np.arccos(np.clip(rel[2,2],-1,1))))})
    r={'name':name,'command_deg':q,'components':rows,'joints':joints,'native_limits':limits,'mate_errors':errors,'max_position_error_mm':max(x['position_error_mm'] for x in rows),'max_angle_error_deg':max(x['angle_error_deg'] for x in rows)};r['kinematic_pass']=not errors and max(r['max_position_error_mm'],r['max_angle_error_deg'])<.001 and all(x['pass'] for x in limits);print({k:v for k,v in r.items() if k not in ['components','native_limits','joints']},flush=True);return r

def main(robot):
    s,d,a,m,build,path=connect_robot(robot);fs=mate_features(d);rows=[]
    for name,q in [('HOME',[0,-25,35,0,0,20]),('J1_POSITIVE',[15,-25,35,0,0,20]),('HOME_RETURN',[0,-25,35,0,0,20])]:
        set_pose(d,fs,q,m['limits'],force=True);r=measure(d,a,m,build,name,q);rows.append(r);(ROOT/f'solidworks/evidence/{robot}_real_limit_probe.json').write_text(json.dumps(rows,indent=2));assert r['kinematic_pass']
    print('Real limit probe passed; not saved yet.',flush=True)
if __name__=='__main__':main(sys.argv[1])
