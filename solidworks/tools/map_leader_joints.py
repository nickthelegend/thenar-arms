from leader_parts import *
from scipy.spatial.transform import Rotation
import yaml,csv
m=manifest();measurements=json.loads((ROOT/'solidworks/evidence/leader_joint_motion_measurements.json').read_text());zero=next(r for r in measurements if r['name']=='ZERO');actual={r['id']:np.array(r['measured_transform_mm']) for r in zero['components']};links={}
for i in m['instances']:
    if i['part'].endswith('_Encoder_L1'):links[i['node']]=actual[i['id']]@np.linalg.inv(matrix(i))
follower=yaml.safe_load((ROOT/'simulation/joint_map.yaml').read_text());rows=[]
for n in m['nodes']:
    if n['joint'] is None:continue
    j=n['joint'];dat=next(a for a in m['nodes'] if a['id']==n['parent']);t=np.linalg.inv(links[dat['parent']])@links[n['id']];logical=follower['joints'][j]['joint_name']
    rows.append({'joint_name':logical,'parent_link':dat['parent'].removeprefix('leader_'),'child_link':n['id'].removeprefix('leader_'),'joint_type':'passive revolute','axis':[0,0,1],'origin_xyz_m':(t[:3,3]*.001).tolist(),'origin_rpy_rad':Rotation.from_matrix(t[:3,:3]).as_euler('xyz').tolist(),'sensor':'AS5600_'+str(j+1),'sensor_i2c_address':'0x36','mux_i2c_address':'0x70','mux_channel':j,'geometric_zero_degrees':0,'firmware_zero_capture_pose':'HOME','home_degrees':m['home'][j],'raw_zero_counts':None,'default_sensor_sign':1,'physical_sensor_sign':'UNVERIFIED','source_range_degrees':m['limits'][j],'physical_range':'UNVERIFIED; source software limits are not hard-stop measurements','follower_target_joint':logical,'conversion':'q = home + sign * signed_wrap_12bit(raw - zero_counts) * 360/4096','drive_ratio':1,'trigger_index_degrees':15 if j==5 else None,'evidence':'CAD measured ZERO plus 28 native mate-driven pose tests; firmware thenar/model.h, calibration.h and thenar.ino'})
(ROOT/'simulation/leader_joint_map.yaml').write_text(yaml.safe_dump({'status':'CAD MEASURED kinematics and SOURCE VERIFIED firmware defaults; physical sensor calibration UNVERIFIED','source_revision':'L1; wrist extension 14mm, trigger mesh mounting index +15deg','joints':rows},sort_keys=False))
fields=['Joint','Parent','Child','Axis','Minimum','Maximum','Zero','Movement PASS/FAIL','Axis PASS/FAIL','Collision result','Mate result','Evidence','Notes']
with (ROOT/'verification/leader_joint_verification.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for j,r in enumerate(rows):
        tests=[p for p in measurements if p['name'].startswith(f'J{j+1}_')];axis=all(x['axis_origin_separation_mm']<.001 and x['axis_tilt_deg']<.001 for p in tests for x in p['joints'])
        writer.writerow(dict(zip(fields,[r['joint_name'],r['parent_link'],r['child_link'],'local +Z',*r['source_range_degrees'],0,'PASS' if all(p['kinematic_pass'] for p in tests) else 'FAIL','PASS' if axis else 'FAIL','Source L1 collision limitations retained; fresh CAD interference classification separate','PASS' if all(not p['mate_errors'] for p in tests) else 'FAIL','solidworks/evidence/leader_joint_motion_measurements.json','Mate-driven articulation only; physical ranges/calibration and mouse dragging unverified'])))
print('Mapped six AS5600 joints to six follower targets.')
