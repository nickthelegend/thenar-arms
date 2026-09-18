"""Publish verified R3 artifacts as a separate prototype, with current reports."""
import json,hashlib,shutil,zipfile
import numpy as np
from scipy.spatial.transform import Rotation
from build_follower_r3 import ROOT,WEB,DEST,context,worlds,matrix,DRIVEN,UNITS

def main():
    build=json.loads((DEST/'build-report.json').read_text())
    fit=json.loads((DEST/'interface-check.json').read_text())
    motion=json.loads((DEST/'motion-check.json').read_text())
    plates=json.loads((DEST/'plate-report.json').read_text())
    screen_path=DEST/'toolpath-screen.json'
    screen=json.loads(screen_path.read_text()) if screen_path.exists() else None
    if screen:
        assert screen.get('files'),'Toolpath screen must identify sliced inputs'
        for path,sha in screen['files'].items():assert hashlib.sha256((DEST/path).read_bytes()).hexdigest()==sha,'Stale toolpath screen: '+path
    sliced_release=bool(screen and screen['all_coarse_screens_passed'] and not any(p['slicer'].get('diagnostics') for p in plates['plates']))
    plates['toolpath_screen']=screen;plates['sliced_downloads_released']=sliced_release
    for p in plates['plates']:
        source=DEST/'plates'/(p['id']+'.3mf')
        assert p['slicer']['input_sha256']==hashlib.sha256(source.read_bytes()).hexdigest(),'Stale slice: '+p['id']
    build['status']='Nominal CAD prototype — no physical validation; sliced toolpaths require review' if not sliced_release else 'Nominal CAD prototype — no physical validation'
    build['pending']=['Physical fit test','Single-shaft load support and retention','Strength, powered operation and cable routing','Encoder leader conversion']+([] if sliced_release else ['Slicer/toolpath review'])
    (DEST/'build-report.json').write_text(json.dumps(build,indent=2))
    (DEST/'plate-report.json').write_text(json.dumps(plates,indent=2))
    assert all(p['watertight'] and p['positive_volume'] and p['shells']==1 for p in build['print_units'])
    # Every check must refer to this exact revision of each printed file.
    for report in [fit,motion]:
        for path,sha in report['files'].items():assert hashlib.sha256((DEST/path).read_bytes()).hexdigest()==sha,path
    assert fit['all_checks_passed'],'An attachment/insertion check failed'
    assert motion['failed_poses']==0,'Internal collision remains'
    target=WEB/'follower-r3';target.mkdir(exist_ok=True)
    for folder in ['print-parts','plates']+(['slicing'] if sliced_release else []):
        if (DEST/folder).exists():shutil.copytree(DEST/folder,target/folder,dirs_exist_ok=True)
    for name in ['build-report.json','interface-check.json','motion-check.json','plate-report.json','MG996R_body_reference.stl','metal_horn_reference.stl']:
        shutil.copy2(DEST/name,target/name)
    shutil.copy2(ROOT/'R3-PRINT.md',target/'READ-ME-FIRST.md')
    if screen:shutil.copy2(screen_path,target/'toolpath-screen.json')
    m=json.loads((DEST/'assembly-source.json').read_text());m['revision']='SO101-MG996R-R3'
    m['status']='Nominal-fit CAD prototype; toolpath review and physical tests pending'
    m['display_base_spacing_mm']=800
    for n in m['nodes']:
        if n['id'] in ['follower','leader']:n['position'][0]=-400 if n['id']=='follower' else 400
    m['parts']=[p for p in m['parts'] if p['kind']!='plate']
    for u in build['print_units']:
        m['parts'].append({'id':u['id'],'label':u['label'],'kind':'print',
            'file':'follower-r3/print-parts/'+u['file'],'bounds':(np.array(u['bounds_mm'])[1]-np.array(u['bounds_mm'])[0]).tolist(),
            'watertight':u['watertight'],'notes':'Original-derived nominal MG996R prototype. '+', '.join(u['source_parts'])})
    for name,label,file,bounds in [('MG996R_body_R3','MG996R · nominal body','MG996R_body_reference.stl',[54,20,42.7]),
                                    ('metal_horn_R3','25T metal horn · Ø20 / 14 mm PCD','metal_horn_reference.stl',[20,20,4.5])]:
        m['parts'].append({'id':name,'label':label,'kind':'hardware','file':'follower-r3/'+file,'bounds':bounds,'watertight':True,'notes':'Purchased component, reference dimensions. Do not print.'})
    w=worlds(m);servos=[i for i in m['instances'] if i['robot']=='follower' and i['part'].startswith('sts3215')]
    child_units={p:name+'_MG996R_R3' for name,members in UNITS.items() for p in members}
    for j,i in enumerate(servos):
        child=next(x for x in m['instances'] if x['robot']=='follower' and x['part']==child_units[DRIVEN[j]])
        t=np.linalg.inv(w[child['node']])@w[i['node']]@matrix(i)
        m['instances'].append({'id':f'follower_metal_horn_{j}','part':'metal_horn_R3','robot':'follower','node':child['node'],
            'position':t[:3,3].tolist(),'rotation':Rotation.from_matrix(t[:3,:3]).as_euler('XYZ',degrees=True).tolist()})
        i['part']='MG996R_body_R3'
    used={i['part'] for i in m['instances']};m['parts']=[p for p in m['parts'] if p['id'] in used]
    for p in m['parts']:p['quantity']={r:sum(i['robot']==r and i['part']==p['id'] for i in m['instances']) for r in ['follower','leader']}
    m['plates']=plates['plates'];m['prototype_reports']={'build':build,'interfaces':fit,'plates':plates}
    # This route must never offer an original leader plate as an MG996R plate.
    assert all(p.get('prototype') and 'MG996R_R3' in p['id'] for p in m['plates'])
    payload=json.dumps(m,indent=2);(target/'manifest.json').write_text(payload);(WEB/'study-manifest.json').write_text(payload)
    poses=[{'name':p['name'],'angles_degrees':p['angles_degrees'],'positive_volume_overlaps':p['overlaps'],
            'table_intersections':p['table_intersections']} for p in motion['poses']]
    ui_report={'status':'NOMINAL PROTOTYPE — physical load testing pending','physical_tested':False,
        'manifest_sha256':hashlib.sha256(payload.encode()).hexdigest(),
        'collisions':{'tested_poses':motion['tested_poses'],'home_interferences':len(poses[0]['positive_volume_overlaps']),
            'failed_sampled_poses':motion['failed_poses'],'table_intersection_poses':motion['table_intersection_poses'],
            'sampled_poses_passed':motion['failed_poses']==0,'full_envelope_passed':False,'poses':poses},
        'method':motion['method'],'print_release_blockers':build['pending']}
    (WEB/'motion-verification.json').write_text(json.dumps(ui_report,indent=2))
    with zipfile.ZipFile(DEST/'SO101-MG996R-R3-PROTOTYPE.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT/'R3-PRINT.md','READ-ME-FIRST.md');z.write(ROOT/'source/LICENSE','LICENSE')
        for folder in ['print-parts','plates']:
            for p in sorted((DEST/folder).glob('*')):
                if p.is_file():z.write(p,p.relative_to(DEST))
        for name in ['build-report.json','interface-check.json','motion-check.json','plate-report.json','MG996R_body_reference.stl','metal_horn_reference.stl']:
            z.write(DEST/name,('reference/'+name if name.endswith('.stl') else 'verification/'+name))
        if screen:z.write(screen_path,'verification/toolpath-screen.json')
        if sliced_release:
            for p in sorted((DEST/'slicing').rglob('*_sliced.3mf')):z.write(p,p.relative_to(DEST))
    shutil.copy2(DEST/'SO101-MG996R-R3-PROTOTYPE.zip',target/'SO101-MG996R-R3-PROTOTYPE.zip')
    print('Published',len(build['print_units']),'printing units on',len(plates['plates']),'plates',flush=True)

if __name__=='__main__':main()
