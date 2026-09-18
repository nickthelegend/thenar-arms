"""Apply display spacing/travel metadata without rebuilding or modifying meshes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT.parent/'robot-studio/public/models/so101'
cfg=json.loads((ROOT/'preview-config.json').read_text())
for path in [ROOT/'output/manifest.json',WEB/'manifest.json',WEB/'study-manifest.json']:
    m=json.loads(path.read_text())
    for n in m['nodes']:
        if n['id'] in ['follower','leader']:
            n['position'][0]=cfg['display_base_spacing_mm']*(-.5 if n['id']=='follower' else .5)
    m['display_base_spacing_mm']=cfg['display_base_spacing_mm']
    if m['revision']=='SO101-clearance-study':
        m.setdefault('upstream_limits',m['limits'])
        m['limits']=cfg['mg996r_limits_degrees'];m['home']=cfg['home_degrees'];m['limits_status']=cfg['limits_status']
    path.write_text(json.dumps(m,indent=2))
hardware=json.loads((ROOT/'purchased-hardware.json').read_text())
(WEB/'purchased-hardware.json').write_text(json.dumps(hardware,indent=2))
for path in [ROOT/'output/clearance-study/fit-analysis.json',WEB/'fit-analysis.json']:
    m=json.loads(path.read_text());m['purchased_hardware']=hardware;path.write_text(json.dumps(m,indent=2))
print('Updated both views: 800 mm display spacing; MG996R study uses provisional ≤170° travel.')
