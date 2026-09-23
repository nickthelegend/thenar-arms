"""Native SolidWorks solid interference at poses previously measured through mates."""
from check_assembly_pose import *
import sys,time
s,doc,asm,cs=connect();rows=[]
poses=json.loads((ROOT/'solidworks/evidence/joint_motion_measurements.json').read_text())
names=['ZERO','HOME','MULTI']+[f'J{j}_{end}' for j in range(1,7) for end in ['MIN','MAX']]
if len(sys.argv)>1:names=[sys.argv[1]]
out=ROOT/'verification/native_solidworks_interference.json'
if out.exists():rows=json.loads(out.read_text())
reverse={c.Name2:id for id,c in cs.items()}
for pose in poses:
    if pose['name'] not in names or any(r['pose']==pose['name'] for r in rows):continue
    assert pose['kinematic_pass']
    manager=typed(asm.InterferenceDetectionManager,'IInterferenceDetectionMgr')
    manager.TreatCoincidenceAsInterference=False;manager.IncludeMultibodyPartInterferences=True
    manager.IgnoreHiddenBodies=True;manager.UseTransform=True
    cslist=[cs[r['id']] for r in pose['components']]
    ts=[sw_transform(s,np.array(r['measured_transform_mm'])) for r in pose['components']]
    result=manager.SetComponentsAndTransforms(com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,cslist),com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,ts))
    print('Checking',pose['name'],'transform setup',result,flush=True);started=time.time()
    try:
        hits=[]
        for hit in manager.GetInterferences() or []:
            hit=typed(hit,'IInterference');cn=[typed(c,'IComponent2').Name2 for c in hit.Components]
            hits.append({'components':cn,'source_ids':[reverse.get(n,n) for n in cn],'volume_mm3':hit.Volume*1e9,'possible_interference':bool(hit.IsPossibleInterference)})
        row={'pose':pose['name'],'joint_degrees':pose['command_deg'],'interferences':hits,'seconds':time.time()-started,'method':'SolidWorks InterferenceDetectionManager on current solid bodies at recorded mate-solved transforms. Coincident faces excluded; multibody checks included.'}
        rows.append(row);out.write_text(json.dumps(rows,indent=2));print('Result',row,flush=True)
    finally:manager.Done()
