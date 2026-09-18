"""Combine verified nominal leader geometry with the existing MG996R follower."""
import json,hashlib,shutil,zipfile
from build_encoder_leader import DEST
from build_follower_r3 import ROOT,WEB

def main():
    check=json.loads((DEST/'verification.json').read_text());build=json.loads((DEST/'build-report.json').read_text())
    enc=json.loads((DEST/'encoder-build.json').read_text());plates=json.loads((DEST/'plate-report.json').read_text())
    plates['sliced_downloads_released']=False
    (DEST/'plate-report.json').write_text(json.dumps(plates,indent=2))
    assert not check['poses'][0]['overlaps'],'Home assembly interference remains'
    assert check['all_interfaces_passed'],'Attachment checks must pass'
    assert check['cartridge_rotation_max_overlap_mm3']<.01 and check['pcb_insertion_max_overlap_mm3']<.01
    for path,digest in check['files'].items():assert hashlib.sha256((DEST/path).read_bytes()).hexdigest()==digest,path
    target=WEB/'encoder-leader-l1';target.mkdir(exist_ok=True)
    for folder in ['print-parts','reference','plates']:(target/folder).mkdir(exist_ok=True)
    rows=build['print_units']+enc['parts']
    for p in rows:
        folder='reference' if p.get('kind')=='hardware' else 'print-parts'
        shutil.copy2(DEST/folder/p['file'],target/folder/p['file'])
    for p in plates['plates']:shutil.copy2(DEST/'plates'/(p['id']+'.3mf'),target/'plates'/(p['id']+'.3mf'))
    for name in ['verification.json','build-report.json','encoder-build.json','plate-report.json']:
        shutil.copy2(DEST/name,target/name)
    if (ROOT/'ENCODER-LEADER.md').exists():shutil.copy2(ROOT/'ENCODER-LEADER.md',target/'READ-ME-FIRST.md')
    shutil.copy2(ROOT/'R3-PRINT.md',WEB/'follower-r3/READ-ME-FIRST.md')
    fit=DEST/'cartridge-fit/plates/P1S_ENCODER_CARTRIDGE_FIT.3mf'
    if fit.exists():
        shutil.copy2(fit,target/fit.name)
        shutil.copy2(DEST/'cartridge-fit/plate-report.json',target/'cartridge-fit-report.json')
        if (DEST/'cartridge-fit/toolpath-screen.json').exists():shutil.copy2(DEST/'cartridge-fit/toolpath-screen.json',target/'cartridge-toolpath-screen.json')
    m=json.loads((WEB/'follower-r3/manifest.json').read_text());leader=json.loads((DEST/'assembly.json').read_text())
    m['nodes']=[n for n in m['nodes'] if not n['id'].startswith('leader')]
    m['instances']=[i for i in m['instances'] if i['robot']=='follower']
    for n in leader['nodes']:
        n['id']=n['id'].replace('follower','leader');n['parent']=n['parent'].replace('follower','leader') if n['parent'] else None
        if n['id']=='leader':n['position'][0]=400
        m['nodes'].append(n)
    for i in leader['instances']:
        i['id']='leader_'+i['id'];i['robot']='leader';i['node']=i['node'].replace('follower','leader');m['instances'].append(i)
    used={i['part'] for i in m['instances']};m['parts']=[p for p in m['parts'] if p['id'] in used]
    for p in rows:
        kind=p.get('kind','print');lo,hi=p['bounds_mm']
        m['parts'].append({'id':p['id'],'label':p['label'],'kind':kind,'file':'encoder-leader-l1/'+('reference/' if kind=='hardware' else 'print-parts/')+p['file'],
            'bounds':[hi[k]-lo[k] for k in range(3)],'watertight':p['watertight'],'notes':'AS5600 passive leader L1. Nominal geometry; physical assembly tests pending.'})
    for p in m['parts']:p['quantity']={r:sum(i['part']==p['id'] and i['robot']==r for i in m['instances']) for r in ['leader','follower']}
    m['revision']='SO101-MG996R-R3-AS5600-L1';m['encoder_leader']={'build':build,'encoder':enc,'verification':check,'plates':plates}
    m['plates']+=plates['plates'];m['status']='MG996R follower R3 + passive AS5600 leader L1; nominal bench prototypes'
    payload=json.dumps(m,indent=2);(WEB/'study-manifest.json').write_text(payload);(target/'manifest.json').write_text(payload)
    motion=json.loads((WEB/'motion-verification.json').read_text());motion['manifest_sha256']=hashlib.sha256(payload.encode()).hexdigest()
    motion['leader']=check;(WEB/'motion-verification.json').write_text(json.dumps(motion,indent=2))
    kit=DEST/'SO101-AS5600-LEADER-L1.zip'
    with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
        for p in rows:
            folder='reference' if p.get('kind')=='hardware' else 'print-parts';z.write(DEST/folder/p['file'],folder+'/'+p['file'])
        for p in plates['plates']:z.write(DEST/'plates'/(p['id']+'.3mf'),'plates/'+p['id']+'.3mf')
        if fit.exists():
            z.write(fit,'test-first/'+fit.name)
            z.write(DEST/'cartridge-fit/plate-report.json','test-first/plate-report.json')
            if (DEST/'cartridge-fit/toolpath-screen.json').exists():z.write(DEST/'cartridge-fit/toolpath-screen.json','test-first/toolpath-screen.json')
        for name in ['verification.json','build-report.json','encoder-build.json','plate-report.json']:z.write(DEST/name,'verification/'+name)
        for p in (ROOT/'firmware').rglob('*'):
            if p.is_file() and '__pycache__' not in str(p):z.write(p,'firmware/'+str(p.relative_to(ROOT/'firmware')))
        z.write(ROOT/'source/LICENSE','licenses/SO101-Apache-2.0.txt')
        z.write(ROOT/'source/encoder/LICENSE.txt','licenses/Adafruit-AS5600.txt');z.write(ROOT/'source/encoder/README-upstream.md','licenses/Adafruit-attribution.md')
        if (ROOT/'ENCODER-LEADER.md').exists():z.write(ROOT/'ENCODER-LEADER.md','READ-ME-FIRST.md')
    shutil.copy2(kit,target/kit.name)
    print('Published follower + encoder leader;',len(m['plates']),'plate layouts')

if __name__=='__main__':main()
